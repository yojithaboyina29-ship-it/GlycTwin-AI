"""
Synthea-Style & IoT Telemetry Data Generator for GlycTwin-AI
Simulates EHR (static) + Wearable continuous telemetry (dynamic 5-min resolution)
Tailored for Indian Type 2 Diabetes (T2D) Demographics & Physiological Profiles.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

def generate_ehr_dataset(num_patients=50):
    """Generates synthetic Electronic Health Records (EHR) for 50 patients."""
    patient_ids = [f"PAT-{1001 + i}" for i in range(num_patients)]
    
    first_names_m = ["Rajesh", "Amit", "Suresh", "Vikram", "Arun", "Sanjay", "Anil", "Deepak", "Rohan", "Sunil"]
    first_names_f = ["Priya", "Sunita", "Anita", "Kavita", "Meena", "Lakshmi", "Pooja", "Deepa", "Ananya", "Ritu"]
    last_names = ["Sharma", "Patel", "Kumar", "Singh", "Rao", "Nair", "Reddy", "Gupta", "Joshi", "Verma"]
    
    data = []
    for pid in patient_ids:
        gender = np.random.choice(["Male", "Female"], p=[0.55, 0.45])
        if gender == "Male":
            name = f"{np.random.choice(first_names_m)} {np.random.choice(last_names)}"
        else:
            name = f"{np.random.choice(first_names_f)} {np.random.choice(last_names)}"
            
        age = int(np.random.normal(52, 10))
        age = max(28, min(78, age))
        
        # South Asian diabetic phenotype: lower BMI threshold for adiposity (visceral fat)
        bmi = round(float(np.random.normal(26.8, 3.5)), 1)
        bmi = max(19.0, min(38.0, bmi))
        
        waist_hip_ratio = round(float(np.random.normal(0.92 if gender == "Male" else 0.86, 0.05)), 2)
        
        # Glycemic indicators
        hba1c = round(float(np.random.normal(8.1, 1.2)), 1)
        hba1c = max(6.2, min(12.5, hba1c))
        
        fasting_glucose = int(np.random.normal(135 + (hba1c - 7.0) * 20, 18))
        fasting_glucose = max(90, min(260, fasting_glucose))
        
        # Lipid profile (High TG, Low HDL pattern common in South Asia)
        triglycerides = int(np.random.normal(195, 45))
        hdl = int(np.random.normal(38 if gender == "Male" else 42, 6))
        ldl = int(np.random.normal(115, 25))
        
        # Renal & blood pressure
        egfr = int(np.random.normal(88, 15))
        systolic_bp = int(np.random.normal(132, 12))
        diastolic_bp = int(np.random.normal(84, 8))
        
        t2d_duration_years = round(float(np.random.exponential(6.0)), 1)
        t2d_duration_years = max(0.5, min(25.0, t2d_duration_years))
        
        # Genetic risk score (scaled 0-1)
        genetic_risk_score = round(float(np.random.beta(3, 3)), 2)
        
        # Primary pharmacotherapy
        med_choices = [
            "Metformin 1000mg",
            "Metformin 1000mg + Glimepiride 2mg",
            "Metformin 1000mg + Dapagliflozin 10mg",
            "Metformin 1000mg + Teneligliptin 20mg",
            "Metformin 1000mg + Insulin Glargine 14U"
        ]
        medication = np.random.choice(med_choices, p=[0.25, 0.30, 0.20, 0.15, 0.10])
        
        # Baseline physiological twin parameters
        # Insulin Sensitivity SI (dL/min/uU)
        insulin_sensitivity = round(float(0.0008 - (bmi - 22) * 0.00002 - (hba1c - 6) * 0.00004), 6)
        insulin_sensitivity = max(0.0002, min(0.0012, insulin_sensitivity))
        
        carb_ratio = int(15 - (hba1c - 7) * 1.5)  # grams per unit insulin
        carb_ratio = max(6, min(20, carb_ratio))
        
        data.append({
            "patient_id": pid,
            "name": name,
            "gender": gender,
            "age": age,
            "bmi": bmi,
            "waist_hip_ratio": waist_hip_ratio,
            "hba1c": hba1c,
            "fasting_glucose_mg_dl": fasting_glucose,
            "triglycerides_mg_dl": triglycerides,
            "hdl_mg_dl": hdl,
            "ldl_mg_dl": ldl,
            "egfr_ml_min": egfr,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "t2d_duration_years": t2d_duration_years,
            "genetic_risk_score": genetic_risk_score,
            "medication_regimen": medication,
            "insulin_sensitivity_si": insulin_sensitivity,
            "insulin_carb_ratio_g_u": carb_ratio
        })
        
    df = pd.DataFrame(data)
    return df


def generate_wearable_telemetry(ehr_df, num_days=14, num_patients_to_simulate=10):
    """
    Generates high-resolution 5-minute sampling IoT sensor stream (CGM, HRV, Sleep, Activity, Meals).
    Incorporates minimal Bergman-like physiological dynamics & circadian rhythms.
    """
    sample_patients = ehr_df.head(num_patients_to_simulate)
    telemetry_records = []
    
    start_date = datetime(2026, 9, 15, 0, 0, 0)
    total_steps_count = int(num_days * 24 * 12) # 5-min intervals per day
    
    for _, patient in sample_patients.iterrows():
        pid = patient["patient_id"]
        base_g = patient["fasting_glucose_mg_dl"]
        si = patient["insulin_sensitivity_si"]
        hba1c = patient["hba1c"]
        
        curr_g = float(base_g)
        active_insulin = 0.0
        active_gut_carbs = 0.0
        
        for t_idx in range(total_steps_count):
            curr_time = start_date + timedelta(minutes=t_idx * 5)
            hour = curr_time.hour
            minute = curr_time.minute
            time_of_day_frac = hour + minute / 60.0
            
            # Sleep stage modeling (23:00 - 07:00)
            is_sleeping = (hour >= 23 or hour < 7)
            if is_sleeping:
                if 2 <= hour < 5:
                    sleep_stage = 2 # Deep sleep
                    hrv = float(np.random.normal(55, 6))
                    hr = float(np.random.normal(58, 4))
                elif 5 <= hour < 7:
                    sleep_stage = 3 # REM sleep
                    hrv = float(np.random.normal(42, 7))
                    hr = float(np.random.normal(64, 5))
                else:
                    sleep_stage = 1 # Light sleep
                    hrv = float(np.random.normal(48, 5))
                    hr = float(np.random.normal(61, 4))
                step_count = int(np.random.choice([0, 0, 0, 5]))
            else:
                sleep_stage = 0 # Awake
                # Awake resting HR & HRV
                base_hrv = 38 - (patient["age"] - 40) * 0.3
                hrv = float(np.random.normal(max(15, base_hrv), 8))
                hr = float(np.random.normal(74 + (10 - hrv/5), 8))
                
                # Activity spikes (walks/exercise)
                if hour in [8, 13, 19] and 15 <= minute <= 45:
                    step_count = int(np.random.normal(350, 80)) # Post-meal walk
                    hr += 25
                    hrv -= 10
                elif np.random.rand() < 0.15:
                    step_count = int(np.random.exponential(120))
                else:
                    step_count = int(np.random.uniform(0, 40))
                    
            step_count = max(0, step_count)
            hrv = max(10.0, min(110.0, hrv))
            hr = max(45.0, min(170.0, hr))
            
            # Meal generation (Indian meal schedule: Breakfast ~08:30, Lunch ~13:30, Dinner ~20:30, Tea snack ~17:00)
            carb_intake = 0.0
            insulin_dose = 0.0
            
            if hour == 8 and minute == 30:
                carb_intake = float(np.random.choice([45, 60, 75, 30])) # idli/dosa/paratha
            elif hour == 13 and minute == 30:
                carb_intake = float(np.random.choice([65, 85, 100, 50])) # rice/roti/dal/curry
            elif hour == 17 and minute == 0:
                carb_intake = float(np.random.choice([10, 25, 35, 40]))  # tea + snacks
            elif hour == 20 and minute == 30:
                carb_intake = float(np.random.choice([60, 80, 95, 55])) # dinner
                
            # If patient is on insulin regimen, inject bolus before large meals (sometimes delayed or omitted to simulate missed dose)
            if "Insulin" in patient["medication_regimen"] and carb_intake >= 50:
                if np.random.rand() > 0.2: # 80% compliance
                    insulin_dose = round(carb_intake / patient["insulin_carb_ratio_g_u"], 1)
                
            # Physiological Glucose Engine simulation step
            # Gut absorption rate
            gut_absorption = active_gut_carbs * 0.09
            active_gut_carbs = max(0.0, active_gut_carbs - gut_absorption + carb_intake * 4.2) # mg equivalent
            
            # Insulin decay & action
            insulin_clearance = active_insulin * 0.10
            active_insulin = max(0.0, active_insulin - insulin_clearance + insulin_dose * 15.0)
            
            # Exercise effect (insulin-independent glucose uptake)
            exercise_effect = (step_count / 100.0) * 1.8
            
            # Dawn Phenomenon effect (cortisol elevation 04:00 - 08:00)
            dawn_effect = 0.0
            if 4 <= hour <= 8:
                dawn_effect = 0.6 * np.sin((time_of_day_frac - 4) / 4.0 * np.pi) * (hba1c / 7.0)
                
            # Autonomic stress effect on liver glucose output (low HRV -> higher cortisol/adrenaline)
            stress_effect = max(0.0, (30.0 - hrv) * 0.08)
            
            # Net glucose rate of change (mg/dL per 5 min)
            dG = (gut_absorption * 0.18) - (active_insulin * si * 800) - exercise_effect + dawn_effect + stress_effect
            # Basal homeostasis return
            dG += (base_g - curr_g) * 0.02
            # Add small random physiological noise
            dG += np.random.normal(0, 0.8)
            
            curr_g += dG
            curr_g = max(45.0, min(380.0, curr_g))
            
            # Calculate stress score
            stress_score = int(np.clip(100 - (hrv * 1.2) + (hr - 70) * 0.5, 1, 100))
            
            telemetry_records.append({
                "patient_id": pid,
                "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                "cgm_glucose": round(curr_g, 1),
                "heart_rate": round(hr, 1),
                "hrv_rmssd": round(hrv, 1),
                "sleep_stage": sleep_stage,
                "step_count_5min": step_count,
                "carb_intake_g": carb_intake,
                "insulin_dose_u": insulin_dose,
                "stress_score": stress_score
            })
            
    df_telemetry = pd.DataFrame(telemetry_records)
    return df_telemetry


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("[1/2] Generating Synthetic EHR Dataset for 50 Indian T2D Patients...")
    ehr_df = generate_ehr_dataset(50)
    ehr_path = os.path.join("data", "ehr_patients.csv")
    ehr_df.to_csv(ehr_path, index=False)
    print(f" Saved EHR dataset to {ehr_path} ({len(ehr_df)} records)")
    
    print("[2/2] Generating Continuous 5-Min Wearable Sensor Stream (14 Days, All 50 Cohort Patients)...")
    telemetry_df = generate_wearable_telemetry(ehr_df, num_days=14, num_patients_to_simulate=50)
    telemetry_path = os.path.join("data", "wearable_telemetry.csv")
    telemetry_df.to_csv(telemetry_path, index=False)
    print(f" Saved Wearable Telemetry dataset to {telemetry_path} ({len(telemetry_df)} time-series samples)")
