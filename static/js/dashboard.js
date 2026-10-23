/* Dashboard Front-end JavaScript logic for GlycTwin-AI */

let currentPatientId = "PAT-1001";
let cgmChart = null;
let telemetryChart = null;
let radarChart = null;

document.addEventListener("DOMContentLoaded", () => {
    initApp();
    bindEventListeners();
});

async function initApp() {
    try {
        const res = await fetch("/api/patients");
        const patients = await res.json();
        
        const select = document.getElementById("patientSelect");
        select.innerHTML = "";
        
        patients.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.patient_id;
            opt.textContent = `${p.patient_id} - ${p.name} (HbA1c: ${p.hba1c}%)`;
            select.appendChild(opt);
        });
        
        if (patients.length > 0) {
            currentPatientId = patients[0].patient_id;
            loadPatientData(currentPatientId);
        }
    } catch (err) {
        console.error("Failed to initialize patient list:", err);
    }
}

function bindEventListeners() {
    document.getElementById("patientSelect").addEventListener("change", (e) => {
        currentPatientId = e.target.value;
        loadPatientData(currentPatientId);
    });
    
    // Sliders label updates
    document.getElementById("sliderCarbs").addEventListener("input", (e) => {
        const val = e.target.value;
        document.getElementById("lblCarbs").textContent = `${val > 0 ? '+' : ''}${val} g`;
    });
    
    document.getElementById("sliderWalk").addEventListener("input", (e) => {
        const val = e.target.value;
        document.getElementById("lblWalk").textContent = `${val} mins`;
    });
    
    document.getElementById("sliderInsulin").addEventListener("input", (e) => {
        const val = parseFloat(e.target.value);
        document.getElementById("lblInsulin").textContent = `${val > 0 ? '+' : ''}${val.toFixed(1)} U`;
    });
    
    // Simulation button
    document.getElementById("btnSimulate").addEventListener("click", runCounterfactualSimulation);
    
    // Metrics Modal
    document.getElementById("btnMetrics").addEventListener("click", () => {
        document.getElementById("metricsModal").classList.remove("hidden");
    });
    
    document.getElementById("closeMetricsModal").addEventListener("click", () => {
        document.getElementById("metricsModal").classList.add("hidden");
    });

    // Add Patient Modal
    const addModal = document.getElementById("addPatientModal");
    document.getElementById("btnAddPatient").addEventListener("click", () => {
        addModal.classList.remove("hidden");
    });
    document.getElementById("closeAddPatientModal").addEventListener("click", () => {
        addModal.classList.add("hidden");
    });
    document.getElementById("btnCancelAdd").addEventListener("click", () => {
        addModal.classList.add("hidden");
    });

    // Add Patient Form Submit
    document.getElementById("addPatientForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const payload = {
            name: document.getElementById("newPatientName").value,
            gender: document.getElementById("newPatientGender").value,
            age: parseInt(document.getElementById("newPatientAge").value),
            bmi: parseFloat(document.getElementById("newPatientBmi").value),
            hba1c: parseFloat(document.getElementById("newPatientHba1c").value),
            fasting_glucose_mg_dl: parseInt(document.getElementById("newPatientFbg").value),
            medication_regimen: document.getElementById("newPatientMed").value
        };

        try {
            const res = await fetch("/api/patient/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            const result = await res.json();
            if (result.status === "success") {
                addModal.classList.add("hidden");
                document.getElementById("addPatientForm").reset();
                
                // Refresh patient list dropdown and select new patient
                await initApp();
                currentPatientId = result.patient.patient_id;
                document.getElementById("patientSelect").value = currentPatientId;
                loadPatientData(currentPatientId);
            }
        } catch (err) {
            console.error("Error creating new patient:", err);
        }
    });
}

async function loadPatientData(patientId) {
    try {
        // 1. Always update static EHR profile card first
        const pRes = await fetch(`/api/patient/${patientId}`);
        if (pRes.ok) {
            const patientData = await pRes.json();
            updatePatientProfileCard(patientData);
            updateRadarChart(patientData);
        }
        
        // 2. Fetch telemetry and predictions
        const res = await fetch(`/api/telemetry/${patientId}?limit_hours=36`);
        if (res.ok) {
            const data = await res.json();
            renderCgmForecastChart(data.historical_telemetry, data.forecast_2h);
            renderWearableTelemetryChart(data.historical_telemetry);
            updateRiskPanel(data.adverse_event_risk);
        }
        
    } catch (err) {
        console.error("Error loading patient data:", err);
    }
}

function updatePatientProfileCard(p) {
    document.getElementById("pName").textContent = p.name;
    document.getElementById("pId").textContent = `${p.patient_id} | ${p.age} yrs`;
    document.getElementById("pGenderBadge").textContent = p.gender;
    document.getElementById("pHba1c").textContent = `${p.hba1c}%`;
    document.getElementById("pFbg").textContent = `${p.fasting_glucose_mg_dl} mg/dL`;
    document.getElementById("pBmi").textContent = `${p.bmi} (WHR ${p.waist_hip_ratio})`;
    document.getElementById("pGenetic").textContent = `${(p.genetic_risk_score * 100).toFixed(0)}% High`;
    document.getElementById("pMedication").textContent = p.medication_regimen;
}

function updateRadarChart(p) {
    const ctx = document.getElementById("radarChart").getContext("2d");
    
    // Normalize axes 0-100
    const glycemicControl = Math.max(10, 100 - (p.hba1c - 6) * 15);
    const autonomicResilience = Math.max(10, 100 - p.age * 0.8);
    const lipidBalance = Math.max(10, 100 - (p.triglycerides / 3.0));
    const renalFunction = Math.min(100, p.egfr_ml_min);
    const insulinSensitivity = Math.min(100, (p.insulin_sensitivity_si / 0.0010) * 100);
    
    if (radarChart) radarChart.destroy();
    
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Glycemic Stability', 'Autonomic Tone', 'Lipid Profile', 'Renal Function', 'Insulin Sensitivity'],
            datasets: [{
                label: 'Physiological Twin State',
                data: [glycemicControl, autonomicResilience, lipidBalance, renalFunction, insulinSensitivity],
                backgroundColor: 'rgba(59, 130, 246, 0.25)',
                borderColor: '#3b82f6',
                borderWidth: 2,
                pointBackgroundColor: '#60a5fa'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: { color: '#94a3b8', font: { size: 9 } },
                    ticks: { display: false, min: 0, max: 100 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderCgmForecastChart(history, forecast, counterfactualForecast = null) {
    const ctx = document.getElementById("cgmForecastChart").getContext("2d");
    
    // Format timestamps & data series
    const labels = history.map(h => h.timestamp.split(" ")[1].slice(0, 5));
    const historyCgm = history.map(h => h.cgm);
    
    const forecastLabels = forecast.map(f => f.timestamp.split(" ")[1].slice(0, 5));
    const allLabels = [...labels, ...forecastLabels];
    
    // Pad array alignment
    const historicalSeries = [...historyCgm, ...Array(forecast.length).fill(null)];
    
    // Forecast series connects from last history point
    const forecastSeries = Array(history.length - 1).fill(null);
    forecastSeries.push(historyCgm[historyCgm.length - 1]);
    forecast.forEach(f => forecastSeries.push(f.cgm_pred));
    
    // Counterfactual series
    let counterSeries = null;
    if (counterfactualForecast) {
        counterSeries = Array(history.length - 1).fill(null);
        counterSeries.push(historyCgm[historyCgm.length - 1]);
        counterfactualForecast.forEach(c => counterSeries.push(c.simulated_pred));
    }
    
    if (cgmChart) cgmChart.destroy();
    
    const datasets = [
        {
            label: 'Historical CGM',
            data: historicalSeries,
            borderColor: '#3b82f6',
            borderWidth: 2.5,
            pointRadius: 0,
            tension: 0.3
        },
        {
            label: '2-Hour AI Forecast',
            data: forecastSeries,
            borderColor: '#a855f7',
            borderWidth: 2.5,
            borderDash: [4, 4],
            pointRadius: 0,
            tension: 0.3
        }
    ];
    
    if (counterSeries) {
        datasets.push({
            label: 'Simulated Counterfactual Twin',
            data: counterSeries,
            borderColor: '#f59e0b',
            borderWidth: 3,
            pointRadius: 0,
            tension: 0.3
        });
    }
    
    cgmChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b', maxTicksLimit: 12, font: { size: 10 } }
                },
                y: {
                    min: 50,
                    max: 300,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { size: 10 } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderWearableTelemetryChart(history) {
    const ctx = document.getElementById("wearableTelemetryChart").getContext("2d");
    
    const labels = history.map(h => h.timestamp.split(" ")[1].slice(0, 5));
    const hrvSeries = history.map(h => h.hrv);
    const stepsSeries = history.map(h => h.steps);
    
    if (telemetryChart) telemetryChart.destroy();
    
    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'HRV RMSSD (ms)',
                    data: hrvSeries,
                    borderColor: '#f43f5e',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    yAxisID: 'yHrv'
                },
                {
                    label: '5-min Steps',
                    data: stepsSeries,
                    backgroundColor: 'rgba(16, 185, 129, 0.3)',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    type: 'bar',
                    yAxisID: 'ySteps'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { display: false },
                yHrv: {
                    type: 'linear',
                    position: 'left',
                    min: 10,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#f43f5e', font: { size: 9 } }
                },
                ySteps: {
                    type: 'linear',
                    position: 'right',
                    min: 0,
                    max: 500,
                    grid: { display: false },
                    ticks: { color: '#10b981', font: { size: 9 } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function updateRiskPanel(risk) {
    document.getElementById("predGlucose2h").textContent = `${risk.predicted_glucose_2h} `;
    document.getElementById("spikeProb").textContent = `${risk.hyperglycemia_spike_prob_percent}% probability of spike >180 mg/dL`;
    
    const badge = document.getElementById("riskBadge");
    const panel = document.getElementById("riskPanel");
    
    badge.textContent = `${risk.risk_level} RISK`;
    
    if (risk.risk_level === "HIGH") {
        badge.className = "text-xs px-2.5 py-0.5 rounded font-bold font-mono bg-rose-500/20 text-rose-400 border border-rose-500/30";
        panel.className = "glass-panel p-5 border-l-4 border-l-rose-500 space-y-4";
        document.getElementById("riskIcon").className = "w-5 h-5 text-rose-400";
    } else if (risk.risk_level === "MODERATE") {
        badge.className = "text-xs px-2.5 py-0.5 rounded font-bold font-mono bg-amber-500/20 text-amber-400 border border-amber-500/30";
        panel.className = "glass-panel p-5 border-l-4 border-l-amber-500 space-y-4";
        document.getElementById("riskIcon").className = "w-5 h-5 text-amber-400";
    } else {
        badge.className = "text-xs px-2.5 py-0.5 rounded font-bold font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
        panel.className = "glass-panel p-5 border-l-4 border-l-emerald-500 space-y-4";
        document.getElementById("riskIcon").className = "w-5 h-5 text-emerald-400";
    }
    
    // Render SHAP drivers list
    const container = document.getElementById("shapDrivers");
    container.innerHTML = "";
    
    risk.primary_drivers.forEach(d => {
        const div = document.createElement("div");
        div.className = "flex justify-between items-center bg-slate-900/40 p-1.5 rounded";
        
        const isPos = d.impact_mg_dl > 0;
        const color = isPos ? "text-rose-400" : "text-emerald-400";
        const sign = isPos ? "+" : "";
        
        div.innerHTML = `
            <span class="text-slate-300">${d.factor}</span>
            <span class="font-mono font-bold ${color}">${sign}${d.impact_mg_dl.toFixed(1)} mg/dL</span>
        `;
        container.appendChild(div);
    });
    
    document.getElementById("cdssText").textContent = 
        risk.risk_level === "HIGH" 
        ? `ALERT: Predicted glucose spike of ${risk.predicted_glucose_2h} mg/dL at t+120m. Recommend immediate 15-min postprandial physical walk to increase insulin-independent glucose clearance, and evaluate a 1.5 Unit bolus insulin adjustment.`
        : `Patient Digital Twin is operating within safe glycemic stability bounds. Maintain standard active lifestyle protocol.`;
}

async function runCounterfactualSimulation() {
    const deltaCarbs = parseFloat(document.getElementById("sliderCarbs").value);
    const deltaWalk = parseFloat(document.getElementById("sliderWalk").value);
    const deltaInsulin = parseFloat(document.getElementById("sliderInsulin").value);
    
    try {
        const res = await fetch("/api/simulate_counterfactual", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                patient_id: currentPatientId,
                delta_carbs_g: deltaCarbs,
                delta_walk_mins: deltaWalk,
                delta_insulin_u: deltaInsulin
            })
        });
        
        const simRes = await res.json();
        
        // Re-fetch telemetry to get base history
        const telRes = await fetch(`/api/telemetry/${currentPatientId}?limit_hours=36`);
        const baseData = await telRes.json();
        
        // Render comparison chart with simulated trajectory overlay
        renderCgmForecastChart(baseData.historical_telemetry, baseData.forecast_2h, simRes.trajectory);
        
        // Update CDSS box text with counterfactual outcome
        document.getElementById("cdssText").innerHTML = `
            <span class="font-bold text-emerald-400 block mb-1">Counterfactual Twin Result:</span>
            ${simRes.cdss_recommendation} (Predicted 2h Glucose: <span class="font-mono font-bold">${simRes.simulated_2h_glucose} mg/dL</span> vs baseline ${simRes.original_2h_glucose} mg/dL).
        `;
        
    } catch (err) {
        console.error("Counterfactual simulation error:", err);
    }
}
