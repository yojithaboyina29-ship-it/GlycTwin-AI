"""
Physiological Digital Twin Core Engine & Multi-Modal Data Fusion Pipeline
Ingests Static EHR Data + Dynamic Wearable Telemetry Time-Series
Computes Digital Twin State & Provides Counterfactual Simulation Capabilities.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class MultiModalFusionEngine:
    """Extracts fused multi-modal time-series features from static EHR + dynamic sensors."""
    
    @staticmethod
    def prepare_fused_dataset(ehr_df, telemetry_df, horizon_steps=24):
        """
        Merges EHR static profiles with Wearable sensor streams.
        horizon_steps = 24 (24 * 5 mins = 120 minutes = 2 hours forecast horizon).
        """
        # Ensure timestamp sorting
        telemetry_df = telemetry_df.sort_values(by=["patient_id", "timestamp"]).copy()
        telemetry_df["timestamp"] = pd.to_datetime(telemetry_df["timestamp"])
        
        fused_rows = []
        
        # Merge static EHR
        df_merged = pd.merge(telemetry_df, ehr_df, on="patient_id", how="inner")
        
        # Group by patient to calculate rolling time-series features
        for pid, group in df_merged.groupby("patient_id"):
            group = group.sort_values(by="timestamp").reset_index(drop=True)
            
            cgm = group["cgm_glucose"].values
            hrv = group["hrv_rmssd"].values
            steps = group["step_count_5min"].values
            carbs = group["carb_intake_g"].values
            insulin = group["insulin_dose_u"].values
            hr = group["heart_rate"].values
            
            n = len(group)
            
            for i in range(24, n - horizon_steps):
                # Current state at time t
                t_stamp = group.loc[i, "timestamp"]
                hour_of_day = t_stamp.hour + t_stamp.minute / 60.0
                
                # Rolling lag features for CGM
                cgm_t = cgm[i]
                cgm_lag_15m = cgm[i - 3]
                cgm_lag_30m = cgm[i - 6]
                cgm_lag_60m = cgm[i - 12]
                cgm_lag_120m = cgm[i - 24]
                
                # Velocity & Acceleration
                velocity_30m = (cgm_t - cgm_lag_30m) / 30.0
                velocity_60m = (cgm_t - cgm_lag_60m) / 60.0
                acceleration_30m = (cgm_t - 2 * cgm_lag_15m + cgm_lag_30m) / 225.0
                
                cgm_roll_mean_1h = np.mean(cgm[i-12:i+1])
                cgm_roll_std_1h = np.std(cgm[i-12:i+1])
                cgm_roll_max_1h = np.max(cgm[i-12:i+1])
                cgm_roll_min_1h = np.min(cgm[i-12:i+1])
                
                # HRV & Stress features
                hrv_t = hrv[i]
                hrv_roll_mean_1h = np.mean(hrv[i-12:i+1])
                hr_roll_mean_1h = np.mean(hr[i-12:i+1])
                
                # Activity sums
                steps_sum_30m = np.sum(steps[i-6:i+1])
                steps_sum_1h = np.sum(steps[i-12:i+1])
                
                # Meals & Insulin exponentially decaying active load
                # Active Carbs On Board (COB) decay model
                cob_weights = np.exp(-0.05 * np.arange(0, 24)[::-1])
                cob = np.sum(carbs[i-23:i+1] * cob_weights)
                
                # Active Insulin On Board (IOB) decay model
                iob_weights = np.exp(-0.03 * np.arange(0, 24)[::-1])
                iob = np.sum(insulin[i-23:i+1] * iob_weights)
                
                # Target at t + 2 hours (120 mins)
                target_g_2h = cgm[i + horizon_steps]
                target_hyper_spike = 1 if target_g_2h >= 180.0 else 0
                target_severe_hyper = 1 if target_g_2h >= 250.0 else 0
                target_hypo_dip = 1 if target_g_2h <= 70.0 else 0
                
                # Circadian features
                sin_time = np.sin(2 * np.pi * hour_of_day / 24.0)
                cos_time = np.cos(2 * np.pi * hour_of_day / 24.0)
                
                fused_rows.append({
                    "patient_id": pid,
                    "timestamp": t_stamp,
                    # Static EHR features
                    "age": group.loc[i, "age"],
                    "bmi": group.loc[i, "bmi"],
                    "waist_hip_ratio": group.loc[i, "waist_hip_ratio"],
                    "hba1c": group.loc[i, "hba1c"],
                    "fasting_glucose": group.loc[i, "fasting_glucose_mg_dl"],
                    "triglycerides": group.loc[i, "triglycerides_mg_dl"],
                    "hdl": group.loc[i, "hdl_mg_dl"],
                    "t2d_duration": group.loc[i, "t2d_duration_years"],
                    "genetic_risk": group.loc[i, "genetic_risk_score"],
                    "insulin_sensitivity": group.loc[i, "insulin_sensitivity_si"],
                    # Dynamic sensor lag features
                    "cgm_t": cgm_t,
                    "cgm_lag_15m": cgm_lag_15m,
                    "cgm_lag_30m": cgm_lag_30m,
                    "cgm_lag_60m": cgm_lag_60m,
                    "cgm_lag_120m": cgm_lag_120m,
                    "velocity_30m": velocity_30m,
                    "velocity_60m": velocity_60m,
                    "acceleration_30m": acceleration_30m,
                    "cgm_roll_mean_1h": cgm_roll_mean_1h,
                    "cgm_roll_std_1h": cgm_roll_std_1h,
                    "cgm_roll_max_1h": cgm_roll_max_1h,
                    "cgm_roll_min_1h": cgm_roll_min_1h,
                    "hrv_t": hrv_t,
                    "hrv_roll_mean_1h": hrv_roll_mean_1h,
                    "hr_roll_mean_1h": hr_roll_mean_1h,
                    "steps_sum_30m": steps_sum_30m,
                    "steps_sum_1h": steps_sum_1h,
                    "active_cob": cob,
                    "active_iob": iob,
                    "sin_time": sin_time,
                    "cos_time": cos_time,
                    # Targets
                    "target_g_2h": target_g_2h,
                    "target_hyper_spike": target_hyper_spike,
                    "target_severe_hyper": target_severe_hyper,
                    "target_hypo_dip": target_hypo_dip
                })
                
        return pd.DataFrame(fused_rows)


class DigitalTwinPhysiologicalSimulator:
    """
    Physiological Digital Twin Simulator allowing real-time 'What-If' counterfactuals.
    Simulates physiological response to interventions (e.g. meal modification, post-meal walks, insulin adjustments).
    """
    
    def __init__(self, trained_model=None):
        self.model = trained_model
        
    def simulate_counterfactual(self, base_features, delta_carbs_g=0.0, delta_walk_mins=0.0, delta_insulin_u=0.0):
        """
        Simulates 2-hour trajectory under modified patient behaviors.
        """
        features = base_features.copy()
        
        # Modify active carbs on board
        si = features.get("insulin_sensitivity", 0.0006)
        hba1c = features.get("hba1c", 8.0)
        
        # Carb impact on 2h forecast (approx +2.2 mg/dL per carb gram for baseline T2D)
        carb_impact = delta_carbs_g * (2.2 * (hba1c / 7.5))
        
        # Physical activity walk impact (-1.5 mg/dL per 10 mins of walking)
        walk_impact = -(delta_walk_mins / 10.0) * (14.0 * (features.get("cgm_t", 140) / 120.0))
        
        # Insulin impact (1 Unit drops glucose by approx ~35-50 mg/dL depending on SI)
        insulin_impact = -(delta_insulin_u * (si * 45000.0))
        
        net_delta = carb_impact + walk_impact + insulin_impact
        
        return net_delta
