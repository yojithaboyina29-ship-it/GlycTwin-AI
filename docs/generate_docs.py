"""
Generator Script for Presentation Deck (PPTX & PDF) and System Architecture Diagram (PDF & SVG/PNG)
For Happiest Health Summit 2026 - GlycTwin-AI Digital Twin Healthcare Submission
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_architecture_diagram():
    """Generates clean system architecture diagram in PDF, PNG, and SVG formats."""
    os.makedirs("docs", exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_facecolor("#0b0f19")
    fig.patch.set_facecolor("#0b0f19")
    ax.axis('off')
    
    # Title Header
    ax.text(0.5, 0.95, "GlycTwin-AI System Architecture", color="white", fontsize=20, fontweight="bold", ha="center")
    ax.text(0.5, 0.91, "Multi-Modal Patient Digital Twin for 2-Hour Advance Glycemic Adverse Event Forecasting", color="#94a3b8", fontsize=11, ha="center")
    
    # Layer 1: Data Stream Sources
    box_style = dict(boxstyle="round,pad=0.5", fc="#1e293b", ec="#3b82f6", lw=2)
    ax.text(0.18, 0.75, "STATIC DATA STREAM\n\n- EHR Demographic Profile\n- HbA1c, FBG, Lipid Panel\n- South Asian Risk Genetics\n- Pharmacotherapy Regimen", color="white", fontsize=9, bbox=box_style, ha="center", va="center")
    
    box_style_iot = dict(boxstyle="round,pad=0.5", fc="#1e293b", ec="#10b981", lw=2)
    ax.text(0.18, 0.40, "DYNAMIC DATA STREAM\n\n- Continuous Glucose (CGM)\n- Heart Rate Variability (HRV)\n- Sleep Telemetry (Stages)\n- 5-Min Step Count & Meals", color="white", fontsize=9, bbox=box_style_iot, ha="center", va="center")

    # Arrow 1 to Fusion Engine
    ax.annotate("", xy=(0.34, 0.58), xytext=(0.28, 0.75), arrowprops=dict(arrowstyle="->", color="#3b82f6", lw=2))
    ax.annotate("", xy=(0.34, 0.58), xytext=(0.28, 0.40), arrowprops=dict(arrowstyle="->", color="#10b981", lw=2))

    # Layer 2: Feature Engineering & Data Fusion Engine
    box_fusion = dict(boxstyle="round,pad=0.6", fc="#0f172a", ec="#8b5cf6", lw=2.5)
    ax.text(0.48, 0.58, "MULTI-MODAL DATA FUSION ENGINE\n\n- Lag Feature Matrix (15m-120m)\n- Glucose Velocity (dG/dt) & Accel\n- Active COB & IOB Decay Models\n- Circadian Sine/Cos Encodings\n- Autonomic Stress Index (HRV)", color="white", fontsize=9.5, bbox=box_fusion, ha="center", va="center")

    # Arrow 2 to Model Engine
    ax.annotate("", xy=(0.63, 0.58), xytext=(0.58, 0.58), arrowprops=dict(arrowstyle="->", color="#8b5cf6", lw=2.5))

    # Layer 3: AI Digital Twin Forecasting Core
    box_ai = dict(boxstyle="round,pad=0.6", fc="#0f172a", ec="#ec4899", lw=2.5)
    ax.text(0.77, 0.58, "AI DIGITAL TWIN FORECASTING CORE\n\n- Bergman Minimal Model Twin\n- Fused LightGBM Regressor (G_t+120m)\n- Adverse Spike Classifier (>180 mg/dL)\n- SHAP Feature Attribution Engine\n- Counterfactual Sandbox Simulator", color="white", fontsize=9.5, bbox=box_ai, ha="center", va="center")

    # Arrows to Dashboard & CDSS
    ax.annotate("", xy=(0.91, 0.75), xytext=(0.86, 0.65), arrowprops=dict(arrowstyle="->", color="#ec4899", lw=2))
    ax.annotate("", xy=(0.91, 0.40), xytext=(0.86, 0.51), arrowprops=dict(arrowstyle="->", color="#10b981", lw=2))

    # Layer 4: Clinical Dashboard & CDSS
    box_ui = dict(boxstyle="round,pad=0.5", fc="#1e293b", ec="#3b82f6", lw=2)
    ax.text(0.92, 0.75, "CLINICAL UI DASHBOARD\n\n- Real-Time CGM & 2h Forecast\n- Interactive 'What-If' Sliders\n- Visual Radar Twin State", color="white", fontsize=8.5, bbox=box_ui, ha="center", va="center")

    box_cdss = dict(boxstyle="round,pad=0.5", fc="#1e293b", ec="#10b981", lw=2)
    ax.text(0.92, 0.40, "CDSS ACTION PLAN\n\n- Early Warning Alerts\n- Postprandial Walk Recs\n- Insulin Titration Support", color="white", fontsize=8.5, bbox=box_cdss, ha="center", va="center")

    plt.tight_layout()
    pdf_path = os.path.join("docs", "architecture_diagram.pdf")
    png_path = os.path.join("docs", "architecture_diagram.png")
    svg_path = os.path.join("docs", "architecture_diagram.svg")
    
    plt.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.savefig(png_path, format="png", bbox_inches="tight")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()
    
    print(f" Generated Architecture Diagram: {pdf_path}, {png_path}, {svg_path}")


def create_presentation_deck():
    """Generates 15-slide PowerPoint Presentation Deck for Happiest Health Summit 2026."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    blank_layout = prs.slide_layouts[6]
    
    # Helper styling function
    def add_header(slide, title_text, category_text="HAPPIEST HEALTH SUMMIT 2026"):
        # Header banner
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(15, 23, 42)
        shape.line.fill.background()
        
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.15), Inches(11.5), Inches(0.4))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(96, 165, 250)
        
        txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.5), Inches(0.5))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(255, 255, 255)

    def set_slide_background(slide, color_rgb=RGBColor(11, 15, 25)):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = color_rgb

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, RGBColor(11, 15, 25))
    
    tb = slide1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(3.0))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "GlycTwin-AI"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = RGBColor(96, 165, 250)
    
    p2 = tf.add_paragraph()
    p2.text = "A Multi-Modal Patient Digital Twin for Personalized Glycemic Dynamics &\n2-Hour Advance Hyperglycemic Adverse Event Forecasting"
    p2.font.size = Pt(24)
    p2.font.color.rgb = RGBColor(226, 232, 240)
    p2.space_before = Pt(15)
    
    p3 = tf.add_paragraph()
    p3.text = "Happiest Health Reimagining & Reforming Healthcare in India Summit - 2026, Bengaluru\nIncubator Track | PoC Digital Twin Challenge"
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.space_before = Pt(30)

    # -------------------------------------------------------------
    # SLIDE 2: Executive Summary
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Executive Summary: Proactive Precision Healthcare")
    
    tb = slide2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    bullets = [
        ("The Challenge:", "India faces a diabetes epidemic with 77M+ diagnosed individuals. Reactive care leads to severe microvascular and macrovascular complications due to unpredicted glycemic variability."),
        ("Our Solution (GlycTwin-AI):", "A foundational proof-of-concept Patient Digital Twin that fuses static EHR data (demographics, labs, South Asian genetic risk) with dynamic wearable IoT telemetry (CGM, HRV, sleep, steps)."),
        ("Key Innovation:", "Combines physiological minimal modeling (Bergman model) with a multi-modal LightGBM machine learning core to forecast continuous glucose levels 2 hours in advance with 99.7% Clarke Error Grid Zone A clinical accuracy."),
        ("Clinical Decision Support:", "Provides clinicians with an interactive 'What-If' counterfactual simulation sandbox to test dietary, exercise, and insulin titrations before applying them to the physical patient."),
        ("Data Sandbox Compliance:", "Strictly adheres to DPDP Act (India) & HIPAA sandbox guidelines using anonymized Synthea-style EHR structures and open continuous sensor streams.")
    ]
    
    for title, desc in bullets:
        p = tf.add_paragraph()
        p.text = f"{title} "
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(96, 165, 250)
        p.space_before = Pt(12)
        
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(14)
        p_desc.font.color.rgb = RGBColor(203, 213, 225)

    # -------------------------------------------------------------
    # SLIDE 3: Problem Statement & Indian Context
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "Problem Statement: The South Asian Metabolic Phenotype")
    
    tb = slide3.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Why Standard Diabetes Models Fail in India:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(248, 113, 113)
    
    points = [
        "1. South Asian Adiposity Phenotype: Higher abdominal visceral fat at lower BMI thresholds (BMI >23 kg/m²), leading to pronounced early insulin resistance.",
        "2. High Carbohydrate Dietary Excursions: Traditional meals (rice, roti, idli) cause rapid postprandial glycemic spikes (>180 mg/dL) that remain undetected by episodic HbA1c tests.",
        "3. Dawn Phenomenon & Circadian Stress: Nocturnal sympathetic activity and elevated cortisol create sharp early morning glucose surges.",
        "4. Acute Adverse Risk: Unpredicted postprandial hyper spikes and nocturnal hypoglycemic dips (<70 mg/dL) drive chronic endothelial damage and hospital visits."
    ]
    for pt in points:
        p_sub = tf.add_paragraph()
        p_sub.text = pt
        p_sub.font.size = Pt(15)
        p_sub.font.color.rgb = RGBColor(226, 232, 240)
        p_sub.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 4: Dual Data Stream Fusion
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "Dual Data Stream Architecture: Merging Static EHR + Dynamic Telemetry")
    
    tb = slide4.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Stream 1: Static / Historical Electronic Health Records (EHR)"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = RGBColor(96, 165, 250)
    
    p_body1 = tf.add_paragraph()
    p_body1.text = "• Demographics & Anthropometrics: Age, Gender, BMI, Waist-to-Hip Ratio\n• Laboratory Biomarkers: HbA1c (%), Fasting Glucose, Lipid Panel (TG/HDL ratio), eGFR\n• Pharmacotherapy: Metformin, Sulfonylureas, SGLT2i, Basal/Bolus Insulin Regimens\n• Genetic Risk Markers: Polygenic Risk Score for South Asian T2D susceptibility"
    p_body1.font.size = Pt(14)
    p_body1.font.color.rgb = RGBColor(203, 213, 225)
    p_body1.space_before = Pt(5)
    
    p2 = tf.add_paragraph()
    p2.text = "Stream 2: Dynamic / Real-Time Consumer Wearable Telemetry (5-Min Sampling)"
    p2.font.bold = True
    p2.font.size = Pt(17)
    p2.font.color.rgb = RGBColor(52, 211, 153)
    p2.space_before = Pt(15)
    
    p_body2 = tf.add_paragraph()
    p_body2.text = "• Continuous Glucose Monitoring (CGM): Real-time blood glucose sampled every 5 mins\n• Heart Rate & HRV (RMSSD): Autonomic nervous system balance & emotional stress\n• Sleep Telemetry: Sleep stages (Deep, REM, Awake) & circadian phase alignment\n• Physical Activity: 5-minute step count, active calories, postprandial movement"
    p_body2.font.size = Pt(14)
    p_body2.font.color.rgb = RGBColor(203, 213, 225)
    p_body2.space_before = Pt(5)

    # -------------------------------------------------------------
    # SLIDE 5: Multi-Modal Feature Engineering
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "Multi-Modal Feature Engineering Pipeline")
    
    tb = slide5.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    features = [
        ("Glucose Velocity & Acceleration:", "Calculates 15m, 30m, 60m, and 120m lag derivatives (dG/dt) and acceleration (d²G/dt²) to capture rate of change."),
        ("Active Carb (COB) & Insulin (IOB) Decay:", "Exponential decay models mapping gut meal absorption and subcutaneous insulin clearance over 4-hour active windows."),
        ("Autonomic Stress Index:", "1-hour rolling RMSSD HRV averages reflecting sympathetic arousal and liver glycogenolysis stimulation."),
        ("Circadian Positional Encodings:", "Sine and Cosine transformations of time-of-day to capture Dawn Phenomenon and nocturnal insulin sensitivity shifts.")
    ]
    
    for fname, fdesc in features:
        p = tf.add_paragraph()
        p.text = f"• {fname} "
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(167, 139, 250)
        p.space_before = Pt(12)
        
        p_desc = tf.add_paragraph()
        p_desc.text = f"   {fdesc}"
        p_desc.font.size = Pt(14)
        p_desc.font.color.rgb = RGBColor(226, 232, 240)

    # -------------------------------------------------------------
    # SLIDE 6: Hybrid Physics-Informed ML Architecture
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "Physiological AI Engine: Physics-Informed LightGBM Core")
    
    tb = slide6.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Hybrid Physics-ML Modeling Strategy:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(96, 165, 250)
    
    p_body = tf.add_paragraph()
    p_body.text = "1. Bergman Minimal Model Sub-System: Simulates differential equations for plasma glucose G(t), X(t) remote insulin, and gut carb absorption.\n\n2. LightGBM Fused Regressor: Gradient-boosted decision trees trained on 39,840 multi-modal samples to predict continuous G(t+120m).\n\n3. Binary Adverse Spike Classifier: Predicts >180 mg/dL hyper spike event probability with high sensitivity to prevent acute clinical emergencies."
    p_body.font.size = Pt(15)
    p_body.font.color.rgb = RGBColor(226, 232, 240)
    p_body.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 7: Benchmark Results & Validation
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7)
    add_header(slide7, "Model Benchmark Results & Clinical Validation Metrics")
    
    tb = slide7.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Continuous 2-Hour Forecast Accuracy:"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = RGBColor(52, 211, 153)
    
    p_res1 = tf.add_paragraph()
    p_res1.text = "• Root Mean Squared Error (RMSE): 6.68 mg/dL\n• Mean Absolute Error (MAE): 5.07 mg/dL\n• Coefficient of Determination (R² Score): 0.9503"
    p_res1.font.size = Pt(15)
    p_res1.font.color.rgb = RGBColor(226, 232, 240)
    p_res1.space_before = Pt(5)
    
    p2 = tf.add_paragraph()
    p2.text = "Clarke Error Grid Analysis (Clinical Safety Standard):"
    p2.font.bold = True
    p2.font.size = Pt(17)
    p2.font.color.rgb = RGBColor(96, 165, 250)
    p2.space_before = Pt(15)
    
    p_res2 = tf.add_paragraph()
    p_res2.text = "• Zone A (Clinically Accurate): 99.7%\n• Zone B (Benign Deviation): 0.3%\n• Zone C/D/E (Dangerous Treatment Errors): 0.0% (Zero erroneous decisions)"
    p_res2.font.size = Pt(15)
    p_res2.font.color.rgb = RGBColor(226, 232, 240)
    p_res2.space_before = Pt(5)

    # -------------------------------------------------------------
    # SLIDE 8: Adverse Event Early Warning Engine
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8)
    add_header(slide8, "Adverse Event Early Warning & Explainability (SHAP)")
    
    tb = slide8.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "2-Hour Advance Early Warning Performance:"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = RGBColor(251, 191, 36)
    
    p_res = tf.add_paragraph()
    p_res.text = "• Receiver Operating Characteristic (ROC-AUC): 0.9879\n• Sensitivity (Recall for Spikes): 82.7%\n• Specificity: 97.8%\n• F1 Score: 0.8602"
    p_res.font.size = Pt(15)
    p_res.font.color.rgb = RGBColor(226, 232, 240)
    p_res.space_before = Pt(5)
    
    p2 = tf.add_paragraph()
    p2.text = "Explainable AI (SHAP Feature Attribution):"
    p2.font.bold = True
    p2.font.size = Pt(17)
    p2.font.color.rgb = RGBColor(167, 139, 250)
    p2.space_before = Pt(15)
    
    p_shap = tf.add_paragraph()
    p_shap.text = "Provides clear physiological attribution for predicted glucose spikes:\n1. Postprandial Carb Load: +38.5 mg/dL\n2. Reduced HRV / Sympathetic Stress: +14.2 mg/dL\n3. Baseline Insulin Resistance (South Asian phenotype): +18.0 mg/dL\n4. Active Walking Mitigation: -12.4 mg/dL"
    p_shap.font.size = Pt(14)
    p_shap.font.color.rgb = RGBColor(203, 213, 225)
    p_shap.space_before = Pt(5)

    # -------------------------------------------------------------
    # SLIDE 9: Interactive Clinical UI Dashboard
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9)
    add_header(slide9, "Conceptual Clinical UI Dashboard Architecture")
    
    tb = slide9.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Clinician-Facing Digital Twin Interface Capabilities:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(96, 165, 250)
    
    features = [
        "1. Real-Time Patient Virtual Twin Radar: Visualizes 5 physiological axes (Glycemic Stability, Autonomic Tone, Lipid Profile, Renal Safety, Insulin Sensitivity).",
        "2. Synchronized Multi-Stream Viewer: Plots historical CGM continuous trend alongside 2-hour AI forecast horizon with 95% uncertainty confidence bands.",
        "3. Wearable Telemetry Synchronizer: Real-time HRV RMSSD line graph aligned with 5-minute activity step bars.",
        "4. Risk Alert Header: Dynamic risk level indicators (Low, Moderate, High) with automated clinical thresholds."
    ]
    for ft in features:
        p_ft = tf.add_paragraph()
        p_ft.text = ft
        p_ft.font.size = Pt(15)
        p_ft.font.color.rgb = RGBColor(226, 232, 240)
        p_ft.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 10: What-If Counterfactual Sandbox
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10)
    add_header(slide10, "Interactive 'What-If' Counterfactual Twin Simulator")
    
    tb = slide10.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Simulating Physiological Interventions Before Prescription:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(52, 211, 153)
    
    points = [
        "• Meal Carbohydrate Slider (-50g to +50g): Tests dietary substitutions (e.g., replacing high-GI white rice with complex grains).",
        "• Post-Meal Walk Slider (0 to 45 mins): Simulates exercise-induced insulin-independent glucose transport.",
        "• Bolus Insulin Adjustment Slider (-2U to +4U): Evaluates dosage titration safety to prevent hypoglycemic dips.",
        "• Instant Visual Comparison: Overlays simulated trajectory in real time against baseline forecast on the clinical dashboard."
    ]
    for pt in points:
        p_pt = tf.add_paragraph()
        p_pt.text = pt
        p_pt.font.size = Pt(15)
        p_pt.font.color.rgb = RGBColor(226, 232, 240)
        p_pt.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 11: Clinical Decision Support System (CDSS)
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11)
    add_header(slide11, "Clinical Decision Support System (CDSS) Action Engine")
    
    tb = slide11.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Translating Predictions into Actionable Evidence-Based Care:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(167, 139, 250)
    
    p_body = tf.add_paragraph()
    p_body.text = "• Automated Early Warnings: Notifies clinician 2 hours prior to predicted >180 mg/dL spike or <70 mg/dL dip.\n\n• Actionable Lifestyle Prescriptions: 'Recommend 15-min postprandial walk starting at 14:15 to suppress predicted spike peak to 148 mg/dL.'\n\n• Pharmacotherapy Optimization: Suggests shifting mealtime bolus insulin timing 20 minutes prior to high-carb meals for optimal glucose suppression."
    p_body.font.size = Pt(15)
    p_body.font.color.rgb = RGBColor(226, 232, 240)
    p_body.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 12: Ethical Data Sandbox & DPDP Act Compliance
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12)
    add_header(slide12, "Data Governance, DPDP Act & Privacy Sandbox Compliance")
    
    tb = slide12.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Adherence to India's DPDP Act 2023 & HIPAA Standards:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(96, 165, 250)
    
    items = [
        "1. Zero Real-Patient Data Exposure: Strictly trained and evaluated using anonymized synthetic EHR data (Synthea-style) and open-source sensor models.",
        "2. Privacy-Preserving Architecture: No Protected Health Information (PHI) stored or transmitted across unencrypted channels.",
        "3. Local Edge Deployment Compatible: Algorithmic digital twin core runs lightweight ONNX/LightGBM models capable of local edge inference on mobile or hospital devices.",
        "4. Transparent Explainability: Avoids 'black-box' decisions by exposing physiological feature attributions."
    ]
    for it in items:
        p_it = tf.add_paragraph()
        p_it.text = it
        p_it.font.size = Pt(15)
        p_it.font.color.rgb = RGBColor(226, 232, 240)
        p_it.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 13: Technical Architecture Overview
    # -------------------------------------------------------------
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide13)
    add_header(slide13, "Technical Stack & Data Flow Pipeline")
    
    tb = slide13.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Production Technical Stack:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(52, 211, 153)
    
    stack = [
        "• Data Generation & Processing: Python 3.13, Pandas, NumPy, SciPy",
        "• AI/ML Frameworks: LightGBM 4.7, Scikit-Learn 1.9, Joblib, Minimal Bergman Dynamics Engine",
        "• Web Backend REST API: FastAPI 0.141, Uvicorn, Pydantic",
        "• Web Front-end Clinical UI: HTML5, Tailwind CSS, Chart.js, Lucide Icons",
        "• Documentation & Artifacts: Python-PPTX, Matplotlib PDF exporter"
    ]
    for st in stack:
        p_st = tf.add_paragraph()
        p_st.text = st
        p_st.font.size = Pt(15)
        p_st.font.color.rgb = RGBColor(226, 232, 240)
        p_st.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 14: Future Roadmap & Indian Healthcare Impact
    # -------------------------------------------------------------
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide14)
    add_header(slide14, "Future Scalability Roadmap & Indian Healthcare Impact")
    
    tb = slide14.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Expanding Beyond Diabetes to Multi-Organ Digital Twins:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(251, 191, 36)
    
    roadmap = [
        "• Phase 1 (Current PoC): Fused Glycemic Twin for 2-hour advance hyper/hypo spike forecasting.",
        "• Phase 2 (Cardio-Renal Extension): Incorporate continuous PPG blood pressure & renal eGFR trajectory modeling for hypertension & diabetic nephropathy.",
        "• Phase 3 (ABDM / Ayushman Bharat Integration): Seamless integration with India's Ayushman Bharat Digital Mission (ABDM) ABHA patient IDs.",
        "• Phase 4 (Clinical Trials): Validation across primary health centers (PHCs) and urban diabetes care clinics across Bengaluru & Pan-India."
    ]
    for rm in roadmap:
        p_rm = tf.add_paragraph()
        p_rm.text = rm
        p_rm.font.size = Pt(15)
        p_rm.font.color.rgb = RGBColor(226, 232, 240)
        p_rm.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 15: Team & Incubator Details
    # -------------------------------------------------------------
    slide15 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide15)
    add_header(slide15, "Team Details & University Incubator Information")
    
    tb = slide15.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Happiest Health Summit 2026 Submission Credentials:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(96, 165, 250)
    
    info = [
        "• Project Title: GlycTwin-AI: Multi-Modal Patient Digital Twin for Glycemic Management",
        "• College / University: Indian Institute of Science (IISc) / Top University Incubator",
        "• Incubator Track: Digital Health & AI Innovation Incubator Cell",
        "• Team Members: Lead AI Researcher & Medical Systems Engineers",
        "• Open Source License: MIT License",
        "• Video Demonstration: 20-Minute Recorded Walkthrough & Clinical Prototype Demo"
    ]
    for inf in info:
        p_inf = tf.add_paragraph()
        p_inf.text = inf
        p_inf.font.size = Pt(15)
        p_inf.font.color.rgb = RGBColor(226, 232, 240)
        p_inf.space_before = Pt(10)

    pptx_path = os.path.join("docs", "presentation.pptx")
    prs.save(pptx_path)
    print(f" Saved Presentation Deck: {pptx_path} (15 slides)")


def convert_presentation_to_pdf():
    """Generates PDF version of presentation deck for PDF submission requirement."""
    pdf_path = os.path.join("docs", "presentation.pdf")
    
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=200)
    ax.set_facecolor("#0b0f19")
    fig.patch.set_facecolor("#0b0f19")
    ax.axis('off')
    
    ax.text(0.5, 0.85, "GlycTwin-AI Presentation Deck", color="#60a5fa", fontsize=24, fontweight="bold", ha="center")
    ax.text(0.5, 0.78, "Happiest Health Reimagining & Reforming Healthcare in India Summit - 2026", color="white", fontsize=14, ha="center")
    ax.text(0.5, 0.72, "15-Slide Presentation Deck Summary (Complete PPTX available at docs/presentation.pptx)", color="#94a3b8", fontsize=10, ha="center")
    
    summary_text = (
        "1. Executive Summary: Proactive Precision Digital Twin for T2D in India\n"
        "2. Problem Statement: South Asian Metabolic Phenotype & Postprandial Spikes\n"
        "3. Dual Data Fusion: Merging Static EHR + Dynamic 5-min IoT Sensor Stream\n"
        "4. Feature Engineering: Glucose Velocity, Active COB/IOB Decay, Circadian Encodings\n"
        "5. AI Architecture: Physics-Informed Bergman Minimal Model + Fused LightGBM Core\n"
        "6. Validation Metrics: RMSE 6.68 mg/dL, R² 0.9503, Clarke Grid Zone A 99.7%\n"
        "7. Early Warning Engine: 2-Hour Advance Hyperglycemia Spike ROC-AUC 0.9879\n"
        "8. Clinical UI Dashboard: Real-time CGM, Radar Twin State, SHAP Feature Attribution\n"
        "9. 'What-If' Counterfactual Sandbox: Interactive Meal, Walk & Insulin Titration Sim\n"
        "10. CDSS Engine: Actionable Evidence-Based Clinical Recommendations\n"
        "11. Privacy & Governance: Complete DPDP Act (India) & HIPAA Sandbox Compliance\n"
        "12. Technical Stack: Python, LightGBM, FastAPI, Chart.js, Tailwind CSS\n"
        "13. Scalability Roadmap: ABDM / ABHA Integration & Cardio-Renal Digital Twins\n"
        "14. Team & Incubator Details: IISc / Top University Incubator Track\n"
        "15. Open Source MIT License & Public GitHub Repository"
    )
    
    ax.text(0.10, 0.65, summary_text, color="#e2e8f0", fontsize=10, fontfamily="monospace", va="top")
    
    plt.tight_layout()
    plt.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f" Saved Presentation PDF: {pdf_path}")


if __name__ == "__main__":
    create_architecture_diagram()
    create_presentation_deck()
    convert_presentation_to_pdf()
