# AI-Driven Forecasting System for Pollution Source Identification and Policy Decision Support — Mumbai

This repository contains an academic prototype for location-based air-quality monitoring, AQI forecasting, pollution-signal analysis and citizen health guidance in Mumbai. It combines a FastAPI backend, a React/Vite citizen interface, model artifacts, datasets, a PostgreSQL-backed station history and a citizen health-advisory retrieval-augmented generation (RAG) pipeline.

The project is intended to support air-quality awareness and future policy analysis. It is not a medical diagnostic system, a regulatory monitoring replacement or a validated source-apportionment instrument.

## What is implemented

| Area | Current implementation |
|---|---|
| Current AQI | Google Air Quality API lookup for a coordinate, including an India CPCB AQI index and pollutant concentrations when returned by the provider |
| Weather | Daily Open-Meteo forecast; an hourly Open-Meteo lookup is also used as context by source analysis |
| AQI forecast | LightGBM inference using current Google AQI, forecast weather, coordinates and a nearest historical-station encoding |
| Station view | Latest records from the PostgreSQL `public.air_quality_data` table, displayed as map markers |
| Source signals | Per-station pollutant-anomaly heuristics for Transport, Road Dust and Industry; scores are not contribution percentages |
| SHAP | A separate endpoint that explains predictions from a configured pollutant-input AQI model |
| Citizen advisory | Profile-based deterministic risk logic wired to citizen-document retrieval, a Groq-hosted structured-output LLM and post-generation checks; the complete RAG experience remains under development |
| Policy Maker interface | Not implemented. The current navigation label is a static placeholder |

The repository's model and data artifacts are not accompanied by verified production evaluation metrics in the active inference code. No accuracy or source-contribution claims are made here.

## Project resources

- [Project synopsis](https://docs.google.com/document/d/126vY7JX1dDhDIRNmvFwCMQNKw8xch68hi0Tn8-m4uVY/edit?usp=sharing)
- [Project presentation](https://www.canva.com/design/DAHBxDm6Ecg/Ym4Isx8m5O_caoRg3RJ43Q/view)
- [Model training notebook](https://colab.research.google.com/drive/1vaZYHteHroeBNMU3cSMXqp8bHuHQ3qbQ?usp=sharing)
- [Initial data gathering and cleaning notebook](https://colab.research.google.com/drive/1adm3dGW53Tu149zRZRNApYujPbeDzGGl?usp=sharing)
- [Data integration notebook](https://colab.research.google.com/drive/1pswhyJXqqTAIymjcNxVoxVEbpnIsz5Vy?usp=sharing)
- [Capstone Project 1 report](https://docs.google.com/document/d/1zrS_-rM8So3qkzWgc2cexOq9dOkRFsQP/edit?usp=sharing&ouid=109023031129947265733&rtpof=true&sd=true)
- [Figma design](https://proud-clad-63688256.figma.site/)
- [Research document](https://docs.google.com/document/d/1rDY83MBeAQXwieENVmpg2IYuJSEuRd1cJ1N1KzCjc08/edit?usp=sharing)
- [IEEE conference paper template](https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn.pdf)

## Goals and source categories

The intended goals are to:

- Monitor and communicate location-based air quality around Mumbai.
- Forecast AQI using weather and current AQI inputs.
- Surface locations with elevated pollution signals.
- Explore pollutant patterns associated with the project's three source categories:
  1. **Transport**
  2. **Road Dust**
  3. **Industry**
- Provide evidence-informed, non-diagnostic citizen health guidance.
- Build toward a policy decision-support interface for government authorities.

The current source-analysis code calls these signal groups `traffic`, `road_dust_construction` and `industry`. The first corresponds to Transport; the second combines Road Dust/Construction indicators and is not a separate fourth source category. These heuristic indicators do not prove a specific emitter or quantify actual source contributions.

## Technology stack

Versions below are those declared in the repository's dependency manifests. Python package pins are in `backend/requirements.txt`; frontend ranges are in `frontend/package.json`.

| Layer | Technologies found in the repository |
|---|---|
| Frontend | React `^19.2.8`, React DOM `^19.2.8`, React Router `^7.18.3`, Vite `^8.2.2`, Tailwind CSS `^4.3.3`, `@tailwindcss/vite` `^4.3.3`, ESLint `^10.9.0` |
| Mapping | Leaflet `^1.9.4`, React Leaflet `^5.0.0`, OpenStreetMap tile URLs |
| Backend/API | Python 3.11 in the scheduled workflow; FastAPI `0.140.0`, Uvicorn `0.51.0`, Pydantic `2.13.4` |
| ML and data processing | LightGBM `4.7.0`, XGBoost `3.2.0`, scikit-learn `1.9.0`, SHAP `0.51.0`, joblib `1.5.3`, pandas `3.0.5`, NumPy `2.2.6` |
| RAG and LLM | LangChain Core `1.7.2`, Community `0.4.2`, Hugging Face integration `1.2.3`, Groq integration `1.1.3`; Groq serves the configured `openai/gpt-oss-120b` model |
| Embeddings/vector store | `sentence-transformers/all-MiniLM-L6-v2`, Hugging Face sentence-transformers `6.2.0`, FAISS CPU `1.15.1` |
| External data providers | Google Air Quality API, Open-Meteo forecast/archive APIs; WAQI and data.gov.in/CPCB provider modules exist but are not wired into the registered routes described below |
| Storage | PostgreSQL via `psycopg2` `2.9.13`; the service code refers to a Neon-hosted PostgreSQL database. CSV and pickle/joblib files are also used |
| Other backend libraries | `httpx` `0.28.1`, `requests` `2.34.2`, `python-dotenv` `1.2.2`, `haversine` `2.9.0` |

No charting library is declared or used by the current pages. AQI and weather values are presented as cards/lists, and stations are shown on a Leaflet map.

## Repository layout

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI route modules registered by main.py
│   │   ├── database/            # PostgreSQL connection helper
│   │   ├── models/              # Pydantic advisory request/response schemas
│   │   ├── rag/                 # Citizen document loading, FAISS retrieval and evidence helpers
│   │   ├── services/            # AQI, weather, prediction, source, advisory and data-provider logic
│   │   └── utils/               # Cache and station-coordinate mapping
│   ├── scripts/                 # Air-quality history ingestion
│   ├── build_rag.py             # Citizen FAISS-index build entry point
│   ├── requirements.txt         # Pinned Python dependencies
│   └── test_*.py                # Standalone diagnostic/retrieval scripts
├── frontend/
│   ├── public/                  # Vite public assets
│   └── src/
│       ├── components/          # AQI, pollutant, forecast, map and advisory UI
│       ├── hooks/               # API-backed page state
│       ├── pages/               # Dashboard, AQI and Health routes
│       ├── services/            # HTTP wrappers for backend endpoints
│       └── utils/               # Default coordinates and AQI/profile options
├── Knowledge_Base_RAG/
│   ├── citizen/                 # AQI, health advisory and health-impact Markdown
│   │   └── vector_store/        # Checked-in FAISS index and pickle metadata
│   └── authority/               # GRAP, mitigation, policy framework and standards Markdown
├── Models/                      # AQI and pollutant-related pickle model artifacts
├── data/
│   ├── Dataset_raw/             # Source air-quality CSVs
│   ├── cleaned/                 # Cleaned station CSVs
│   ├── final/                   # Consolidated dataset exports
│   ├── integrated with weather/ # Integrated air-quality/weather data
│   ├── Model_Dataset/           # AQI prediction and pollutant/SHAP datasets
│   └── stations/                # Station coordinates and encoded IDs
├── docs/                        # Capstone report and synopsis PDFs
└── .github/workflows/           # Scheduled hourly AQI ingestion workflow
```

### Important files

| File | Purpose |
|---|---|
| `backend/app/main.py` | Creates the FastAPI application, registers all routers, and defines `GET /` |
| `backend/app/api/*.py` | HTTP route definitions; route behavior is summarized in the API reference |
| `backend/app/services/air_quality_service.py` | Calls the Google provider and parses its current AQI response |
| `backend/app/services/prediction_service.py` | Loads the configured LightGBM artifact, assembles the 13 model features and returns daily forecasts |
| `backend/app/services/source_identification_service.py` and `source_calculation.py` | Query recent station observations and calculate robust pollutant-anomaly signals |
| `backend/app/services/personalization_service.py` | Deterministic AQI/profile risk and activity guidance |
| `backend/app/services/advisory_llm_service.py` and `advisory_validator.py` | Build structured LLM output and apply post-generation safeguards |
| `backend/app/services/providers/google_air_quality_provider.py` | Google current-conditions and forecast HTTP client; current-condition results are cached in memory |
| `backend/app/services/providers/weather_provider.py` | Open-Meteo daily and hourly weather requests |
| `backend/app/services/providers/waqi_provider.py`, `cpcb_provider.py` | Additional provider code not called by the active routes |
| `backend/app/rag/` | Citizen Markdown loading, AQI-aware chunk construction, vector-store loading and evidence retrieval/ranking |
| `backend/scripts/ingest_air_quality.py` | Fetches Google historical data for configured Mumbai-area coordinates and writes station records to PostgreSQL |
| `backend/build_rag.py` | Rebuilds the citizen FAISS index from eligible Markdown files |
| `frontend/src/App.jsx` | Registers the Dashboard, AQI and Health client routes |
| `frontend/src/pages/` | The three implemented citizen pages |
| `frontend/src/services/` | Browser-side wrappers for current AQI, station data, forecasts, weather and advisory requests |
| `frontend/vite.config.js` | Local development proxy for `/api`, `/prediction` and `/weather` to `127.0.0.1:8000` |
| `data/Model_Dataset/aqi_prediction_dataset.csv` | Historical station/weather/AQI data used for station mapping during inference |
| `data/stations/stations.csv` | Station coordinate/encoding lookup |
| `Models/` | Four checked-in model artifacts; only the configured artifacts loaded by services are used at runtime |

The checked-in model files are `Models/aqi_lightgbm_lag1.pkl`, `Models/aqi_xgb_lag1.pkl`, `Models/aqi_xgb_model.pkl` and `Models/pollutant_source_model.pkl`. The active prediction service loads a LightGBM artifact selected by `AQI_MODEL_PATH`; the two XGBoost files have no active service references. `pollutant_source_model.pkl` may be intended for the SHAP service, but its expected package structure has not been verified. `data/Model_Dataset/pollutant_shap_dataset.csv` is also present; no active endpoint reads it.

The raw, cleaned and consolidated data directories contain more files than shown in this summary. The full data rows and the contents of the report PDFs were not used to infer runtime behavior.

## Backend architecture and data providers

`backend/app/main.py` registers these routers directly: health, station, pollution, weather, prediction, air quality, SHAP, advisory, source identification and analytics. There is no separate API router for policy recommendations.

### Current air quality

`GET /api/air-quality/current` calls `air_quality_service.get_current()`, which calls the Google Air Quality API current-conditions endpoint and parses the response. The request location is passed as latitude/longitude coordinates. The parser chooses the `ind_cpcb` index for `aqi`, category and dominant pollutant, and also returns the `uaqi` value when present. Its response is marked `model_based: true`; it is a coordinate-based provider result, not a direct reading from the project's station database.

The returned pollutant map is based on pollutant codes in the Google response. The parser does not impose a fixed list; common codes include PM2.5, PM10, NO2, SO2, CO and O3, and can include other provider codes. Values reported in parts per billion are converted to micrograms per cubic metre only for codes with configured molecular weights. The response includes source, timestamp, region, AQI display/category/scale, dominant pollutant and pollutant values/units. No independent AQI-category calculation is applied to this endpoint.

The Google current-condition provider caches responses in process memory for 15 minutes using coordinates rounded to three decimal places. There is no persistent cache or explicit fallback provider in this call path. The WAQI and data.gov.in/CPCB modules are present but are not imported by the active current-air-quality route.

### Station records and ingestion

`GET /api/pollution/current` reads the most recent record for each station ID from `public.air_quality_data` in PostgreSQL and returns station coordinates, AQI/category, pollutant values, timestamp, color and data source. The scheduled job in `.github/workflows/hourly-air-quality.yml` runs `backend/scripts/ingest_air_quality.py` hourly (cron minute 10 UTC) and can also be started manually. The script requests the previous three hours from Google's history endpoint at 20 hard-coded station coordinates, normalizes pollutant units, stores the records and removes records older than 31 days. It does not collect readings from a direct CPCB monitor feed.

The table is expected to exist before ingestion or API use; no schema-creation/migration file was found in the inspected source. The 30-day analytics and source-analysis queries depend on this same table and database.

### Weather

The daily weather service calls Open-Meteo with the requested coordinates and `Asia/Kolkata` timezone. Available daily fields are maximum, minimum and mean temperature; mean relative humidity; maximum and mean wind speed; dominant wind direction; mean sea-level pressure; and precipitation sum. Missing provider values can be returned as `null`.

The source-analysis path separately requests hourly temperature, relative humidity, precipitation, wind speed/direction and pressure for the observation hour. This hourly result is contextual prose, not a pollutant correction or source-attribution score. Source analysis reads station coordinates from a CSV; its default `STATION_MAPPING_PATH` is a machine-specific `E:\Capstone\...` path, so configure it to this repository's `data/stations/stations.csv` for local use.

## AQI forecasting

The registered `GET /prediction/forecast` route calls, in order:

1. The current Google air-quality service for the supplied latitude/longitude.
2. The daily Open-Meteo weather service for the requested forecast period.
3. `prediction_service.predict_future_aqi()` for LightGBM inference.

The service loads its model using `AQI_MODEL_PATH`; the active service is implemented as LightGBM inference. It uses `HISTORICAL_DATASET_PATH` to find the geographically nearest historical station and its `station_encoded` value. Historical AQI rows are not fed as a time series into this inference function. Instead, the current Google AQI is reused as `AQI_lag1` for every forecast day.

The model input has these 13 features:

```text
temperature_2m_mean
relative_humidity_2m_mean
wind_speed_10m_mean
wind_speed_10m_max
wind_direction_10m_dominant
pressure_msl_mean
precipitation_sum
month
dayofyear
latitude
longitude
station_encoded
AQI_lag1
```

The endpoint accepts `forecast_days` from 1 through 7 (default 3). The forecast is a daily list of `{date, predicted_AQI}` records, together with current AQI, location and historical-station mapping details. Negative predictions are clipped to zero. Model performance metrics are not emitted by this service and are not asserted in this README.

The repository also contains `aqi_xgb_lag1.pkl` and `aqi_xgb_model.pkl`; no active service reference to those files was found. The checked-in `aqi_lightgbm_lag1.pkl` is the candidate artifact for the active prediction service, but the service selects its model exclusively through `AQI_MODEL_PATH`.

## Pollution source signals and explainability

The source-identification routes query up to 30 days of station records from PostgreSQL. For each station, the service compares the latest observation with earlier records from the same year and month. A pollutant baseline is only calculated when at least 10 usable baseline samples exist. The service uses the median and median absolute deviation (MAD), converts the current deviation to a robust normalized score, clamps it to `[-1, 1]`, then averages relevant signals into the source groups:

| Project category | Code key | Signals used |
|---|---|---|
| Transport | `traffic` | NO2 and CO anomalies |
| Road Dust | `road_dust_construction` | PM10 and coarse-particle (`PM10 - PM2.5`, floored at zero) anomalies |
| Industry | `industry` | SO2 anomaly |

Unavailable or insufficient measurements produce missing scores. The API labels each score as above, below or around usual levels and includes data-coverage and baseline-sample information. It also optionally attaches same-hour weather context.

These are **pollutant-anomaly heuristics**, not a trained sector-contribution model, chemical source apportionment, measured emission fractions or proof of a source. The code does not calculate sector contribution percentages. Station coordinates are returned, but there is no spatial hotspot clustering or sector-specific hotspot algorithm. The source-analysis endpoint is not currently consumed by the citizen frontend.

`GET /shap/current` is a separate explainability path. It gets current pollutant concentrations from Google, feeds them to a configured saved model, and returns that model's predicted AQI plus per-feature SHAP values and direction. It explains the configured model's prediction; it does not explain Google’s returned AQI, nor does it attribute pollution to Transport, Road Dust or Industry. The service expects `SHAP_MODEL_PATH` to load a joblib package containing `model` and `features`. The checked-in `Models/pollutant_source_model.pkl` is a possible intended artifact, but its serialized structure was not loaded or verified during this documentation task.

## Citizen health advisory

The frontend form collects:

- Age group: `18-30 years`, `31-50 years`, `51-65 years` or `65+ years`.
- One or more health-condition options, or `None`: asthma, COPD/chronic lung condition, other respiratory condition, heart/cardiovascular condition, diabetes, allergies/sinusitis, pregnancy or other/not listed.
- Activity level: Light, Moderate or Heavy Activity.
- Browser-provided latitude and longitude after the user grants geolocation permission.

`POST /api/advisory/` accepts an `AdvisoryRequest` with `age_group`, `health_conditions` (a list, default empty), `activity_level`, `latitude` and `longitude`. The route then:

1. Fetches current Google AQI for the submitted location.
2. Classifies AQI using the CPCB bands in `aqi_service.py`.
3. Computes deterministic profile risk and an activity recommendation in `personalization_service.py`.
4. Retrieves AQI/profile-relevant citizen documents from the FAISS index.
5. Requests a structured advisory from Groq using `openai/gpt-oss-120b`.
6. Applies deterministic post-generation checks and returns the result plus evidence metadata.

The AQI classification bands are 0–50 Good, 51–100 Satisfactory, 101–200 Moderate, 201–300 Poor, 301–400 Very Poor and above 400 Severe. The deterministic personalization uses AQI, age group, conditions and activity level. The LLM supplies structured prose, but its prompt restricts it to the supplied profile, deterministic assessment and retrieved evidence; it prohibits diagnosis, prescriptions and unsupported recommendations. The validator overwrites the returned risk level with the deterministic value, removes certain medication-related recommendations, caps list lengths and supplies a disclaimer if absent. These safeguards are code checks, not a medical review or guarantee of factual correctness.

The response contains `user_profile`, `location`, `air_quality`, `aqi_classification`, `personalized_risk`, `advisory` and an `evidence` array (source/category/topic/AQI bounds). `advisory` follows `AdvisoryResponse`: risk level, summary, today's recommendations, activity timing, outdoor exposure, protective measures, warning signs, evidence source filenames and disclaimer.

This is general air-pollution guidance, not medical diagnosis or treatment. The browser currently requires at least one selected health-condition state (including the `None` choice), although the backend request model allows an empty list.

## RAG pipeline — current status

The citizen RAG path is wired into the advisory endpoint but remains under development. The active flow in `backend/app/rag/` is:

1. `document_loader.py` reads Markdown under `Knowledge_Base_RAG/citizen/` and skips README files. Authority documents are not loaded by this loader.
2. `vector_store.py` splits document text on lines and creates AQI-aware chunks; this is not a generic fixed-size/recursive text splitter.
3. AQI range detection assigns `aqi_min`/`aqi_max`; keyword rules assign a `topic`. Source, category and filename metadata are carried forward.
4. The builder embeds chunks with `sentence-transformers/all-MiniLM-L6-v2` and saves a LangChain FAISS store under `Knowledge_Base_RAG/citizen/vector_store/`.
5. At request time, `retriever.py` loads the local FAISS store, performs similarity search with an expanded candidate count, retains general evidence and AQI-range-applicable evidence, and `evidence_ranker.py` ranks by AQI, health condition, activity and topic. The advisory retriever returns the top `k` documents (the API requests 3).
6. The LLM service formats the retrieved documents into a prompt, requests strict structured output using the Pydantic response schema, and passes the result through the advisory validator.

Citizen documents currently present are in `aqi_information/`, `health_advisories/` and `health_impacts/`. The `authority/` tree contains GRAP, mitigation, policy-framework and standards documents, but the current citizen loader does not include them. A checked-in `index.faiss` and `index.pkl` exist; whether those files are current with all source documents was not verified. The runtime loader uses `allow_dangerous_deserialization=True`, so only load a vector store you trust.

`evidence_filter.py` and `evidence_selector.py` contain additional line/document filtering helpers, but they are not called in the active `retrieve_advisory_evidence()` → LLM route. The active pipeline uses semantic retrieval, AQI metadata filtering and heuristic ranking; the optional selector does not currently filter the LLM context. Output validation is limited to the explicit checks in `advisory_validator.py`.

Backend `test_*.py` files are primarily direct-run retrieval/inspection scripts, not a configured automated test suite. Some scripts exercise the pipeline and print results; no model-quality or medical-safety benchmark is reported here.

### Future Policy Maker RAG

No policy RAG endpoint or policy recommendation service is registered. The authority Markdown corpus is present but is not loaded by the current citizen RAG pipeline. A future Policy Maker RAG pipeline is intended to retrieve relevant government and policy evidence, then provide traceable recommendations in context of AQI, the three project source categories, observed locations/hotspots and source documentation. That workflow must be implemented and validated before it is represented as an existing capability.

## Frontend — Citizen interface

The React app registers `/dashboard`, `/aqi` and `/health`. `Navbar.jsx` links these pages and shows a non-interactive “Policy Maker” label; there are no Policy Maker routes or screens.

| Page | Current content and API use |
|---|---|
| Dashboard | Requests current AQI and station records in parallel through `useAirQuality`, and requests a three-day AQI forecast through `usePrediction`. Shows AQI, pollutant cards, forecast rows and a Leaflet station map. |
| AQI | Uses the same current AQI, station and forecast calls, and separately requests a two-day weather forecast. Displays AQI, pollutants, forecast rows, a small set of weather fields and the station map. |
| Health | Collects profile selections, requests browser geolocation on submit, and posts to `/api/advisory/`. Displays the returned risk, summary, recommendations, activity/exposure guidance, protective measures, warning signs, evidence filenames and disclaimer. |

The default Dashboard/AQI coordinates are fixed at `19.076, 72.8777`; they are not obtained from the browser. The Health page uses device coordinates for its advisory. The map uses station records from PostgreSQL and OpenStreetMap tiles; its markers are distinct from the user-coordinate Google AQI result. The application currently contains no time-series charts.

The reusable components include `AQICard`, `PollutantCard`, `ForecastCard`, `WeatherImpact`, `MapCard`, `ProfileForm`, `AdvisoryResult`, `LoadingState`, `ErrorState` and `SectionHeader`. The map can be expanded/collapsed. Current AQI cards map the provider's `aqi`, `aqi_display`, category and dominant pollutant; forecast rows map `forecast[].predicted_AQI`; map markers map each station's coordinates and fields; the weather card displays selected fields from the first forecast day; and the advisory result maps the structured `advisory` fields and backend location/AQI.

The hooks show loading and error states; current AQI and forecast requests can be retried, while weather/advisory errors are displayed without a retry control. API errors are logged to the browser console and shown as generic user-facing messages. Several page labels describe data as “live” or station readings, but the code's ingestion path stores Google Air Quality API history at configured coordinates, and the station endpoint's `data_source` is the authoritative field for those records.

## Policy Maker interface — development status

The intended navigation is **Overview**, **Source Analysis**, **Policy Simulator** and **Reports**. None of those Policy Maker screens is implemented. The current “Policy Maker” navbar item is only static text.

Backend functionality that a future interface could reuse includes current station records, AQI forecasting, per-station heuristic source signals and 30-day station analytics. The frontend does not currently call the source-identification or analytics routes. There is no implemented policy simulator, intervention-impact model, government-facing recommendation endpoint or authority-document RAG flow. Future recommendations should identify their supporting evidence and clearly separate heuristic signals from measured contributions.

## API reference

All routers below are registered in `backend/app/main.py`. Query names and response fields are based on the route/service code, not inferred from UI mockups.

| Endpoint | Method | Inputs | Purpose / main response fields | Frontend consumer | Status |
|---|---|---|---|---|---|
| `/` | GET | None | Backend status message | None | Implemented |
| `/health/` | GET | None | `status`, `message` | None | Implemented |
| `/station/?lat=...&lon=...` | GET | Required latitude and longitude | Nearest CSV station: `station`, `station_encoded`, coordinates, `distance_km` | None | Implemented |
| `/api/pollution/current` | GET | None | `source`, `count`, `stations[]`; latest database station fields include coordinates, timestamp, AQI/category, color, pollutants and `data_source` | Dashboard, AQI map | Implemented; requires PostgreSQL data |
| `/weather/forecast?latitude=...&longitude=...&forecast_days=...` | GET | Coordinates required; days 1–10, default 2 | Coordinates, actual record count as `forecast_days`, `source`, `forecast[]` of date and daily weather fields | AQI page | Implemented |
| `/prediction/forecast?latitude=...&longitude=...&forecast_days=...` | GET | Coordinates required; days 1–7, default 3 | Source label, current AQI/category/pollutants and forecast fields: `historical_station`, `station_encoded`, `mapping_distance_km`, `forecast[]` (`date`, `predicted_AQI`) | Dashboard, AQI | Implemented; requires configured model/data and provider access |
| `/api/air-quality/current?lat=...&lon=...` | GET | Latitude -90..90 and longitude -180..180 | Parsed Google current AQI, category, dominant pollutant, universal AQI and pollutant map | Dashboard, AQI | Implemented; requires Google key |
| `/shap/current?latitude=...&longitude=...` | GET | Coordinates required | Current AQI/provider fields and `shap_analysis` (`predicted_aqi`, pollutant `contributions[]`) | None | Implemented behind compatible configured model |
| `/api/advisory/` | POST | JSON: `age_group`, `health_conditions[]`, `activity_level`, `latitude`, `longitude` | Profile, location, air quality, AQI classification, deterministic risk, structured advisory and retrieved evidence metadata | Health | Wired; RAG/LLM behavior remains under development and needs external keys/index |
| `/api/source-identification/` | GET | None | `source`, `method`, `count`, per-station pollutant anomalies, heuristic source scores, coverage, weather context and status | None | Implemented heuristic; requires PostgreSQL |
| `/api/source-identification/{station_id}` | GET | Path `station_id` (for example `station_0`) | One station result with the same fields as above; 404 if no station data | None | Implemented heuristic; requires PostgreSQL |
| `/api/analytics/history/{station_id}` | GET | Path `station_id` | 30-day hourly series, station, period, timezone, record count, pollutants and `data[]` | None | Implemented; requires PostgreSQL |

Errors are raised as HTTP errors by the route handlers (including provider, database, model and advisory failures). Exact error status varies by endpoint; clients should not assume a successful response shape on failure.

## System data flows

### A. Citizen dashboard

```text
React Dashboard/AQI
  ├─ GET /api/air-quality/current
  │    └─ Google Air Quality API → parser/cache → current AQI and pollutants
  └─ GET /api/pollution/current
       └─ PostgreSQL air_quality_data → latest row per station → map markers
```

The dashboard's AQI and station markers are separate data paths. A failure in either parallel request currently makes the combined `useAirQuality` request state show an error.

### B. AQI forecasting

```text
React page → GET /prediction/forecast
  → Google current AQI + Open-Meteo daily weather
  → nearest station mapping from historical CSV
  → LightGBM (13 features; current AQI reused as AQI_lag1)
  → daily predicted_AQI records → forecast cards
```

### C. Citizen personalized advisory

```text
Health form → browser coordinates/profile → POST /api/advisory/
  → Google current AQI → CPCB AQI classification
  → deterministic profile risk
  → citizen FAISS retrieval + AQI filter + evidence ranking
  → Groq structured output → validator → advisory + evidence metadata
```

This path is present in code but depends on correct environment configuration, the checked-in/current vector store, network access and a Groq API key. It is not a medical diagnosis or treatment flow.

### D. Future Policy Maker workflow — planned

```text
Existing AQI / forecast / source-signal / station-history APIs
  → future Overview, Source Analysis, Policy Simulator and Reports UI
  → future authority-document retrieval and evidence-backed recommendations
```

Only the existing APIs/data at the start of this flow are implemented. Policy screens, intervention simulation and policy RAG are planned, not current behavior.

## Installation and local execution

The backend's active service modules load model artifacts while the application imports. Configure the required paths and provider/database values before starting the API. The checked-in `backend/.env.example` is empty, so it does not provide a ready-to-copy configuration.

### Backend

From the repository root in PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a local `backend/.env` (do not commit credentials) and fill in real values:

```dotenv
GOOGLE_AIR_QUALITY_API_KEY=replace-with-google-air-quality-key
DATABASE_URL=postgresql://<username>:<password>@<hostname>:5432/<database>
AQI_MODEL_PATH=..\Models\aqi_lightgbm_lag1.pkl
HISTORICAL_DATASET_PATH=..\data\Model_Dataset\aqi_prediction_dataset.csv
SHAP_MODEL_PATH=..\Models\pollutant_source_model.pkl
STATION_MAPPING_PATH=..\data\stations\stations.csv
GROQ_API_KEY=replace-with-groq-key
```

Notes:

- `AQI_MODEL_PATH` and `SHAP_MODEL_PATH` are read during application import. The SHAP artifact must be a joblib package with the `model` and `features` entries expected by `shap_service.py`; verify that the selected artifact matches before relying on this endpoint.
- `HISTORICAL_DATASET_PATH` is needed by AQI prediction and other historical-data service code.
- `DATABASE_URL` must point to a PostgreSQL database with the expected `public.air_quality_data` table and records. No schema migration is included in the inspected source.
- `STATION_MAPPING_PATH` should point to `data/stations/stations.csv`; the source-analysis default is a machine-specific path.
- `GOOGLE_AIR_QUALITY_API_KEY` is required for current AQI, prediction and ingestion. `GROQ_API_KEY` is required when generating a citizen advisory.
- `WAQI_TOKEN`, `DATA_GOV_API_KEY` and `RESOURCE_ID` are referenced by provider modules that are not wired to the registered active routes.
- The repository declares Python dependencies, but does not declare a universal local Python version. The scheduled workflow uses Python 3.11.

Start the backend from `backend/`:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend: `http://127.0.0.1:8000`

Swagger UI: `http://127.0.0.1:8000/docs`

### Frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite: `http://localhost:5173`. Its development proxy forwards `/api`, `/prediction` and `/weather` to `http://127.0.0.1:8000`. For another deployment, `VITE_API_BASE_URL` can set the HTTP base URL; do not put secrets in frontend environment variables.

Other declared frontend scripts are `npm run build`, `npm run lint` and `npm run preview`.

### Rebuild the citizen vector store

From `backend/`, after installing dependencies:

```powershell
python build_rag.py
```

This rebuild reads Markdown under `Knowledge_Base_RAG/citizen/`, downloads/uses the configured sentence-transformer model as needed and writes the FAISS artifacts to `Knowledge_Base_RAG/citizen/vector_store/`. It does not index the `authority/` documents.

## Limitations and future scope

### Current limitations verified in code

- Current AQI is obtained from a coordinate-based Google API and is marked model-based; it is not a direct reading from the repository's station-history table.
- The Dashboard and AQI pages use fixed default coordinates; only the Health page requests browser geolocation.
- Station data, analytics and source analysis require a reachable PostgreSQL database and the expected table.
- Source signals are pollutant-anomaly heuristics. They do not quantify contributions, confirm sources or detect spatial hotspots.
- SHAP explains a configured model's output, not the live provider AQI or the three project source categories.
- The citizen RAG chain is wired but depends on an external LLM, local FAISS data and retrieval metadata; its extra evidence selector/filter modules are not used in the active route.
- `STATION_MAPPING_PATH` defaults to a developer-specific Windows location and must be overridden for a local checkout if hourly weather context is desired in source analysis.
- The UI presents no chart-based historical trends and does not yet expose source analysis, SHAP or station analytics.
- No evaluation metrics are emitted by the active AQI inference endpoint. The accuracy/validity of model artifacts and source-signal interpretations needs separate validation.
- The checked-in advisory scripts are primarily diagnostics, not a comprehensive automated API/integration test suite.

### Future scope

- Complete and evaluate the Citizen RAG retrieval, grounding and output-validation workflow.
- Implement the Policy Maker interface with Overview, Source Analysis, Policy Simulator and Reports.
- Build a separate Policy Maker RAG workflow over authority documents, with source citations and evidence traceability.
- Improve and validate sector-specific analysis for Transport, Road Dust and Industry; do not present signals as source contributions without a validated method.
- Develop spatial hotspot analysis and sector-specific station views.
- Add evidence-based policy recommendations based on appropriate government reports, source signals and AQI conditions.
- Implement policy intervention simulation only after suitable models and supporting data are developed and validated.
- Add historical reporting and analytics as dependable, quality-controlled data becomes available.

## Verified Implementation Status

| Feature | Status | Actual implementation/files | Available for frontend integration? |
|---|---|---|---|
| Current location AQI and pollutant fields | Implemented | `api/air_quality.py`, `services/air_quality_service.py`, Google provider/parser | Yes; already used by Dashboard and AQI |
| Station map data | Implemented, database-dependent | `api/pollution.py`, `services/pollution_service.py`, PostgreSQL `air_quality_data` | Yes; already used by Dashboard and AQI |
| Daily AQI forecast | Implemented, model/configuration-dependent | `api/prediction.py`, `services/prediction_service.py`, LightGBM artifact and historical CSV | Yes; already used by Dashboard and AQI |
| Daily/hourly weather | Implemented | `api/weather.py`, `services/weather_service.py`, Open-Meteo provider | Yes; daily route already used by AQI |
| Source identification | Partial: anomaly-based signals, not attribution percentages | `api/source_identification.py`, `services/source_identification_service.py`, `services/source_calculation.py` | Yes, after database/configuration setup; not yet consumed by UI |
| Station history analytics | Implemented, database-dependent | `api/analytics.py`, `services/analytics_service.py` | Yes; not yet consumed by UI |
| Pollutant SHAP explanation | Implemented behind a compatible configured model | `api/shap.py`, `services/shap_service.py` | Yes; not yet consumed by UI |
| Citizen deterministic personalization | Implemented | `api/advisory.py`, `services/aqi_service.py`, `services/personalization_service.py` | Yes; called by Health |
| Citizen RAG + LLM advisory | Partially implemented / under development | `rag/`, `services/advisory_llm_service.py`, `services/advisory_validator.py`, citizen FAISS store | Wired to Health; requires operational retrieval, Groq key and validation |
| Policy Maker UI | Planned; not implemented | Static “Policy Maker” text in `frontend/src/components/Navbar.jsx`; no page/routes | No |
| Policy Maker RAG/recommendations | Planned; not implemented | Authority documents exist under `Knowledge_Base_RAG/authority/`; not loaded by active RAG | No |
| Policy simulator | Planned; not implemented | No simulator route/service/page found | No |

## Documentation verification notes

- This README was checked against the route registration, API/service implementations, model-loading code, frontend routes/hooks/services/components, dependency manifests, environment-variable references, RAG modules, knowledge-base/vector-store directory, data/model file inventory and the hourly-ingestion workflow.
- Not every raw CSV row, binary model payload, FAISS pickle payload or report-PDF page was inspected. The serialized SHAP artifact's schema, model evaluation metrics, historical dataset provenance/quality, database schema/availability, live provider output and vector-store freshness therefore need independent verification.
- No model-performance values, source percentages, unimplemented endpoints or policy capabilities are asserted.
- Known frontend/backend differences: Dashboard/AQI use fixed coordinates while advisory uses browser coordinates; the navbar's Policy Maker label has no route; the frontend does not call source-analysis, SHAP, nearest-station or analytics endpoints; the UI's station-monitoring wording should be interpreted in light of the Google-history ingestion source; and the frontend requires a health-condition selection even though the backend accepts an empty list.
