# Maharashtra GRAP Response Framework: AQI Categories, Thresholds, and Escalation Logic

**Source:** Maharashtra Graded Response Action Plan — Official Implementation Framework  
**Mandated by:** Hon'ble National Green Tribunal (NGT), Order dated 20/11/2019 (Application No. 681/2018)  
**Implementing Body:** City-Level Implementation Committee under NCAP, constituted via Government Resolution No. NCA 2018/CR.196(2)/T.C.2, dated 18/09/2019  
**Category:** Authority — GRAP Framework Reference  

---

## 1. Purpose and Legal Basis

The Maharashtra GRAP is an Emergency Response System developed under direction of the National Green Tribunal (NGT). It provides a **graded, AQI-threshold-based protocol** that mandates specific pollution control actions by responsible authorities when ambient air quality deteriorates beyond defined levels.

The framework is structured so that **actions under lower severity stages continue to remain in force when a higher stage is triggered**. All stages are cumulative and additive.

GRAP applies to all **Non-Attainment Cities (NACs)** in Maharashtra — cities that have exceeded National Ambient Air Quality Standards (NAAQS) for at least one pollutant for five or more consecutive years. Mumbai, Navi Mumbai, Vasai-Virar, and Thane are among the designated NACs.

---

## 2. AQI Pollutant Measurement Reference

The GRAP framework uses **24-hour ambient PM₂.₅ and PM₁₀ concentrations** as the primary trigger parameters. AQI is also informed by data from:
- **SAFAR (System of Air Quality and Weather Forecasting and Research)** — provides real-time and forecast AQI data for Maharashtra cities
- **IITM (Indian Institute of Tropical Meteorology)** — provides meteorological forecast inputs to SAFAR
- **MPCB (Maharashtra Pollution Control Board)** — day-to-day monitoring of ambient AQI levels

GRAP stage activation is based on **prevailing AQI combined with forecast AQI**. If forecast AQI is projected to reach the threshold of the next stage, the Task Force may pre-emptively invoke the next stage.

---

## 3. Maharashtra GRAP: Four Severity Categories

### CATEGORY I — Moderate to Poor

| Parameter | Trigger Range |
|-----------|--------------|
| PM₂.₅ (24-hr ambient) | 61 – 120 µg/m³ |
| PM₁₀ (24-hr ambient) | 101 – 350 µg/m³ |
| AQI Range (approx.) | Moderate to Poor |

**Condition description:** Air quality is deteriorating beyond satisfactory levels. Pollution sources are active and generating measurable excess particulate matter. Early-stage enforcement and source control are required to prevent escalation.

---

### CATEGORY II — Very Poor

| Parameter | Trigger Range |
|-----------|--------------|
| PM₂.₅ (24-hr ambient) | 121 – 250 µg/m³ |
| PM₁₀ (24-hr ambient) | 351 – 430 µg/m³ |
| AQI Range (approx.) | Very Poor (AQI ~301–400) |

**Condition description:** Air quality poses health risks to the general population. Pollution has reached levels where source reduction alone is insufficient — demand-side management (transport, DG sets, parking disincentives) is required in addition to continued Category I measures.

---

### CATEGORY III — Severe

| Parameter | Trigger Threshold |
|-----------|------------------|
| PM₂.₅ (24-hr ambient) | 250+ µg/m³ |
| PM₁₀ (24-hr ambient) | 430+ µg/m³ |
| AQI Range (approx.) | Severe (AQI ~401–450) |

**Condition description:** Air quality is severely degraded. High-emission industrial sources must be shut down. Public transport must be augmented to substitute for restricted private vehicle use. All Category I and II measures remain in force.

---

### CATEGORY IV — Emergency / Severe+

| Parameter | Trigger Threshold |
|-----------|------------------|
| PM₂.₅ (24-hr ambient) | 300 µg/m³ or above, **persisting for 48 hours or more** |
| PM₁₀ (24-hr ambient) | 500 µg/m³ or above, **persisting for 48 hours or more** |
| AQI Range (approx.) | Emergency / Severe+ (AQI >450) |

**Condition description:** A sustained pollution emergency. The duration criterion (48 hours) is critical — this is not a momentary spike but a persistent episode that indicates meteorological stagnation and systemic emission excess. Hardest restrictions apply. The Task Force has authority to impose additional shutdowns beyond the prescribed list.

---

## 4. Trigger Logic and Escalation Rules

### Rule 1: Cumulative Escalation
When a higher severity category is invoked, **all actions from all previous categories remain active**. Actions are additive across stages. For example:
- Category III is active → Category I + Category II + Category III actions all apply simultaneously
- Category IV is active → all four categories' actions apply simultaneously

### Rule 2: Forecast-Based Pre-Emptive Activation
GRAP stages may be **pre-emptively invoked** based on projected/forecast AQI reaching the next stage's threshold, even before the actual measurement crosses the threshold. This allows authorities to get ahead of deteriorating conditions. Forecast inputs come from:
- SAFAR app (IITM-based air quality forecast)
- MPCB day-to-day monitoring and projections

### Rule 3: Minimum Active Duration
Once invoked, GRAP actions **continue to be implemented for a minimum of 15 days** from the date of invocation, or until ambient AQI returns below the stage threshold — whichever is later. Authorities cannot prematurely de-escalate within the 15-day window without Task Force approval.

### Rule 4: Task Force Authority to Modify
The Task Force Committee at the city level has authority to:
- Revise the GRAP or add additional measures
- Make improvements and exceptions to the GRAP schedule based on the prevalent situation and forecast AQI levels
- Invoke any additional steps including shutting of activities, institutes, or offices not specified in the standard GRAP schedule

### Rule 5: 48-Hour Duration for Emergency Trigger
Category IV (Emergency) requires the **PM₂.₅ ≥ 300 µg/m³ or PM₁₀ ≥ 500 µg/m³ condition to persist for at least 48 continuous hours**. A single-day spike does not trigger Category IV — sustained multi-day pollution episodes at these levels are required.

---

## 5. Escalation Decision Framework

```
Measure current PM₂.₅ and PM₁₀ (24-hr average)
         │
         ▼
PM₂.₅ < 61 µg/m³ AND PM₁₀ < 101 µg/m³?
  └─ YES → Satisfactory/Good range. Standard monitoring only.
  └─ NO → Continue below
         │
         ▼
PM₂.₅ 61–120 µg/m³ OR PM₁₀ 101–350 µg/m³?
  └─ YES → ACTIVATE CATEGORY I (Moderate to Poor)
  └─ NO → Continue below
         │
         ▼
PM₂.₅ 121–250 µg/m³ OR PM₁₀ 351–430 µg/m³?
  └─ YES → ACTIVATE CATEGORY II (Very Poor) + retain Category I
  └─ NO → Continue below
         │
         ▼
PM₂.₅ > 250 µg/m³ OR PM₁₀ > 430 µg/m³?
  └─ YES → ACTIVATE CATEGORY III (Severe) + retain I + II
  └─ NO → Continue below
         │
         ▼
PM₂.₅ ≥ 300 µg/m³ OR PM₁₀ ≥ 500 µg/m³
AND this condition has persisted for ≥ 48 hours?
  └─ YES → ACTIVATE CATEGORY IV (Emergency) + retain I + II + III
```

---

## 6. Maharashtra vs. National AQI Scale Mapping

The Maharashtra GRAP uses PM₂.₅/PM₁₀ concentration thresholds directly. These approximately correspond to the national CPCB AQI scale as follows:

| Maharashtra GRAP Category | PM₂.₅ Range | PM₁₀ Range | CPCB AQI Approx. | CPCB Category |
|--------------------------|-------------|-----------|------------------|---------------|
| Pre-GRAP (baseline) | 31–60 µg/m³ | 51–100 µg/m³ | 51–100 | Satisfactory |
| Pre-GRAP (baseline) | 61–90 µg/m³ | 101–250 µg/m³ | 101–200 | Moderate |
| **Category I: Moderate to Poor** | **61–120 µg/m³** | **101–350 µg/m³** | **~101–300** | **Moderate–Poor** |
| **Category II: Very Poor** | **121–250 µg/m³** | **351–430 µg/m³** | **~301–400** | **Very Poor** |
| **Category III: Severe** | **250+ µg/m³** | **430+ µg/m³** | **~401–450** | **Severe** |
| **Category IV: Emergency** | **300+ µg/m³ (48h+)** | **500+ µg/m³ (48h+)** | **>450** | **Severe+/Emergency** |

> **Note:** Maharashtra's Category I begins at PM₂.₅ 61 µg/m³ — lower than the CPCB "Poor" threshold (90 µg/m³). Maharashtra GRAP is therefore more stringent in its early-stage activation.

---

## 7. Monitoring and Alert Trigger Infrastructure

| Source | Role in GRAP Trigger |
|--------|----------------------|
| MPCB Continuous Ambient Air Quality Monitoring Stations (CAAQMS) | Primary real-time PM₂.₅ and PM₁₀ measurement |
| SAFAR App (IITM-based) | Forecast AQI projections used for pre-emptive stage invocation |
| IMD / IITM | Meteorological forecasts (wind, temperature inversion, humidity) informing dispersion conditions |
| CPCB National AQI Bulletin | Reference data and national-level alert cross-checking |
| Task Force Committee | Decision authority for stage invocation and de-escalation |

---

## 8. Key Principles for Authority Agents

1. **Thresholds are concentration-based, not AQI-index-based.** Always refer to PM₂.₅ and PM₁₀ µg/m³ values for precise stage determination.
2. **GRAP is additive.** Never de-escalate lower-stage actions when a higher stage is active.
3. **15-day minimum rule.** Once activated, stages stay active for at minimum 15 days.
4. **Forecast matters.** If forecast shows AQI will cross the next threshold within 24–48 hours, pre-emptive invocation of the next stage is appropriate.
5. **Task Force has override authority.** The Committee can extend, expand, or modify any GRAP action at any stage.
6. **Emergency (Category IV) requires persistence, not just peak.** A single spike to 300 µg/m³ PM₂.₅ does not trigger Category IV — it must sustain for 48 hours.
