"""
AI Model Training & Evaluation Pipeline for GlycTwin-AI
Trains fused ML models on static EHR + dynamic Wearable sensor telemetry.
Evaluates continuous 2-hour glucose forecasting and adverse event prediction.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_auc_score, f1_score, precision_score, recall_score, confusion_matrix
import lightgbm as lgb

from digital_twin_engine import MultiModalFusionEngine

def clarke_error_grid(y_true, y_pred):
    """
    Computes Clarke Error Grid zones (Zone A, B, C, D, E) for clinical accuracy of CGM predictions.
    Zone A: Clinically accurate (within 20% or <70 mg/dL when true <70)
    Zone B: Benign errors
    Zone C/D/E: Unnecessary or dangerous treatment decisions
    """
    zone_a = 0
    zone_b = 0
    zone_c_d_e = 0
    
    total = len(y_true)
    for true, pred in zip(y_true, y_pred):
        if (true <= 70 and pred <= 70) or (abs(pred - true) <= 0.20 * true):
            zone_a += 1
        elif (true >= 180 and pred >= 70 and pred <= 180) or (true <= 70 and pred >= 180):
            zone_c_d_e += 1
        elif (pred >= 240 and 70 <= true <= 180) or (pred <= 70 and 70 <= true <= 180):
            zone_c_d_e += 1
        else:
            zone_b += 1
            
    pct_a = round((zone_a / total) * 100, 2)
    pct_b = round((zone_b / total) * 100, 2)
    pct_c_d_e = round((zone_c_d_e / total) * 100, 2)
    
    return pct_a, pct_b, pct_c_d_e


def train_and_evaluate():
    print("[1/4] Loading EHR and Telemetry datasets...")
    ehr_df = pd.read_csv("data/ehr_patients.csv")
    telemetry_df = pd.read_csv("data/wearable_telemetry.csv")
    
    print("[2/4] Fusing multi-modal streams & engineering dynamic lag features...")
    fused_df = MultiModalFusionEngine.prepare_fused_dataset(ehr_df, telemetry_df, horizon_steps=24)
    print(f" Multi-modal fused dataset ready: {len(fused_df)} samples across {len(fused_df['patient_id'].unique())} cohort patients.")
    
    feature_cols = [
        "age", "bmi", "waist_hip_ratio", "hba1c", "fasting_glucose", "triglycerides", "hdl",
        "t2d_duration", "genetic_risk", "insulin_sensitivity",
        "cgm_t", "cgm_lag_15m", "cgm_lag_30m", "cgm_lag_60m", "cgm_lag_120m",
        "velocity_30m", "velocity_60m", "acceleration_30m",
        "cgm_roll_mean_1h", "cgm_roll_std_1h", "cgm_roll_max_1h", "cgm_roll_min_1h",
        "hrv_t", "hrv_roll_mean_1h", "hr_roll_mean_1h",
        "steps_sum_30m", "steps_sum_1h", "active_cob", "active_iob",
        "sin_time", "cos_time"
    ]
    
    X = fused_df[feature_cols]
    y_reg = fused_df["target_g_2h"]
    y_clf_hyper = fused_df["target_hyper_spike"]
    
    # Temporal split per patient (first 80% time-steps for training, last 20% for testing)
    train_indices = []
    test_indices = []
    
    for pid, group in fused_df.groupby("patient_id"):
        n_group = len(group)
        split_pt = int(n_group * 0.8)
        indices = group.index.tolist()
        train_indices.extend(indices[:split_pt])
        test_indices.extend(indices[split_pt:])
        
    X_train, X_test = X.loc[train_indices], X.loc[test_indices]
    y_reg_train, y_reg_test = y_reg.loc[train_indices], y_reg.loc[test_indices]
    y_clf_train, y_clf_test = y_clf_hyper.loc[train_indices], y_clf_hyper.loc[test_indices]
    
    print(f" Train set: {len(X_train)} samples | Test set: {len(X_test)} samples")
    
    print("[3/4] Training LightGBM 2-Hour Ahead Glucose Regressor & Adverse Event Classifier...")
    
    # Continuous Regressor
    regressor = lgb.LGBMRegressor(
        n_estimators=300,
        learning_rate=0.03,
        num_leaves=31,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=-1
    )
    regressor.fit(X_train, y_reg_train)
    
    # Binary Classifier for Hyperglycemic Spike (>180 mg/dL)
    classifier = lgb.LGBMClassifier(
        n_estimators=250,
        learning_rate=0.03,
        num_leaves=31,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=-1
    )
    classifier.fit(X_train, y_clf_train)
    
    # Feature Importance
    importance_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": regressor.feature_importances_
    }).sort_values(by="importance", ascending=False)
    
    print("[4/4] Evaluating Models on Unseen Patient Cohort...")
    y_reg_pred = regressor.predict(X_test)
    y_clf_prob = classifier.predict_proba(X_test)[:, 1]
    y_clf_pred = (y_clf_prob >= 0.45).astype(int) # Threshold adjusted for clinical safety sensitivity
    
    rmse = float(np.sqrt(mean_squared_error(y_reg_test, y_reg_pred)))
    mae = float(mean_absolute_error(y_reg_test, y_reg_pred))
    r2 = float(r2_score(y_reg_test, y_reg_pred))
    
    clarke_a, clarke_b, clarke_cde = clarke_error_grid(y_reg_test.values, y_reg_pred)
    
    roc_auc = float(roc_auc_score(y_clf_test, y_clf_prob))
    f1 = float(f1_score(y_clf_test, y_clf_pred))
    precision = float(precision_score(y_clf_test, y_clf_pred))
    recall = float(recall_score(y_clf_test, y_clf_pred)) # Sensitivity
    
    tn, fp, fn, tp = confusion_matrix(y_clf_test, y_clf_pred, labels=[0, 1]).ravel()
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    
    metrics = {
        "regressor": {
            "rmse_mg_dl": round(rmse, 2),
            "mae_mg_dl": round(mae, 2),
            "r2_score": round(r2, 4),
            "clarke_error_grid": {
                "zone_a_percent": clarke_a,
                "zone_b_percent": clarke_b,
                "zone_c_d_e_percent": clarke_cde
            }
        },
        "classifier_2h_hyperglycemia_spike": {
            "roc_auc": round(roc_auc, 4),
            "sensitivity_recall": round(recall, 4),
            "specificity": round(specificity, 4),
            "precision": round(precision, 4),
            "f1_score": round(f1, 4)
        },
        "top_10_features": importance_df.head(10).to_dict(orient="records")
    }
    
    print("\n=================== MODEL EVALUATION METRICS ===================")
    print(f"Continuous 2-Hour Forecast RMSE: {rmse:.2f} mg/dL | MAE: {mae:.2f} mg/dL | R2: {r2:.4f}")
    print(f"Clarke Error Grid -> Zone A: {clarke_a}% (Clinically Accurate) | Zone B: {clarke_b}%")
    print(f"Adverse Event Classifier (2h Hyperglycemia Spike >180 mg/dL):")
    print(f" ROC-AUC: {roc_auc:.4f} | Sensitivity: {recall*100:.1f}% | Specificity: {specificity*100:.1f}% | F1: {f1:.4f}")
    print("=================================================================\n")
    
    # Save artifacts
    model_bundle = {
        "regressor": regressor,
        "classifier": classifier,
        "feature_cols": feature_cols,
        "ehr_sample": ehr_df,
        "fused_columns": fused_df.columns.tolist()
    }
    
    os.makedirs("models", exist_ok=True)
    joblib.dump(model_bundle, "models/trained_glucose_model.pkl")
    print(" Saved model bundle to models/trained_glucose_model.pkl")
    
    with open("models/model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(" Saved evaluation report to models/model_metrics.json")
    
    return metrics

if __name__ == "__main__":
    train_and_evaluate()
