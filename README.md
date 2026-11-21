
# VayuSuchak
## AI-Driven Pollution Source Identification, Forecasting & Policy Decision Support Dashboard for Mumbai

<p align="center">
  An AI-powered air quality intelligence platform for monitoring pollution,
  forecasting future AQI levels, identifying potential pollution sources,
  and supporting informed environmental decision-making.
</p>

---

## Project Documentation & Presentation

| Resource | Link |
|---|---|
| Project Report | [Report](https://github.com/Madhu-Wala/AI-Driven-Forecasting-System-for-Pollution-Source-Identification-and-Policy-Decision-Support) |
| Project Presentation (PPT) | [Presentation](https://docs.google.com/presentation/d/1dnhZrcr3A9o9wrczXguAogY0_UC04pUN/edit?usp=sharing&ouid=114725319132321397156&rtpof=true&sd=true) |
| Project Demonstration Video | [Video](https://drive.google.com/drive/folders/1fL83CazwrLBA_vHcQ8pG5mo8Jhcf9czg) |
| GitHub Repository | [Repository](https://github.com/Madhu-Wala/AI-Driven-Forecasting-System-for-Pollution-Source-Identification-and-Policy-Decision-Support) |


---

## 1. Project Overview

VayuSuchak is an AI-driven air quality monitoring and decision-support platform developed with a focus on Mumbai. The system integrates air quality data, machine learning-based forecasting, research-guided pollution source identification, interactive visualizations, and Retrieval-Augmented Generation (RAG) to provide useful environmental insights to citizens and policymakers.

Conventional air quality applications primarily display current AQI values and pollutant concentrations. However, understanding the reasons behind pollution levels, anticipating future changes, and translating environmental information into actionable decisions remain important challenges.

VayuSuchak addresses these challenges through a unified platform that provides:

- Real-time air quality monitoring using available air quality data sources.
- Interactive visualization of monitoring stations and their pollution levels.
- Machine learning-based AQI forecasting.
- Research-guided identification of potential pollution source categories.
- Historical air quality trends and hotspot analysis.
- Citizen-oriented health advisories.
- Policy-oriented insights and recommendations supported by a knowledge base.

The platform provides two main interfaces:

**Citizen Portal:** Provides location-based air quality information, forecasts, pollutant details, trends, and health advisories.

**Policy Maker Portal:** Provides station-level pollution analysis, source identification results, policy insights, and evidence-supported recommendations. Access to policymaker authentication and protected operations is restricted to authorized users.

VayuSuchak is designed as a decision-support system. Its outputs are intended to assist interpretation and planning rather than replace official environmental assessments or regulatory decisions.

---

## 2. Problem Statement

Urban air pollution is influenced by several interacting factors, including vehicular emissions, industrial activities, construction, road dust, and changing environmental conditions.

Although air quality monitoring data is available from different sources, citizens and decision-makers often lack a unified platform that combines current pollution information, future predictions, potential source identification, and practical recommendations.

The absence of integrated analytical support makes it difficult to:

- Understand current air quality conditions at specific locations.
- Identify potential categories of pollution contributing to observed pollutant variations.
- Anticipate future AQI changes.
- Examine historical pollution patterns and station-level hotspots.
- Provide accessible health guidance to citizens.
- Support policymakers with organized environmental evidence.

**Proposed Solution:**

VayuSuchak integrates data processing, machine learning, geospatial visualization, research-guided source identification, and RAG-based advisory generation into a single platform for Mumbai's air quality monitoring and decision support.

---

## 3. Project Objectives

1. Develop a centralized platform for monitoring air quality across selected Mumbai monitoring stations.
2. Display current AQI and individual pollutant concentrations through an interactive dashboard.
3. Develop a machine learning model to forecast future AQI levels.
4. Identify potential pollution source categories using station-specific pollutant behaviour and historical baselines.
5. Visualize historical air quality patterns, trends, and pollution hotspots.
6. Provide location-based health advisories for citizens.
7. Provide policymakers with relevant environmental evidence and policy-oriented recommendations.
8. Integrate multiple data sources and analytical modules into a scalable full-stack application.

---

## 4. Key Features

### 4.1 Citizen Portal

- Location-based air quality information using device geolocation.
- Current AQI and associated air quality category.
- Individual pollutant information, including PM2.5, PM10, NO2, SO2, CO, and O3, where available.
- Interactive monitoring station map.
- AQI forecasting using the trained machine learning model.
- Historical air quality trends.
- Weather information associated with the selected location.
- RAG-based health advisories and pollution-related guidance.

### 4.2 Policy Maker Portal

- Protected policymaker login and registration.
- Monitoring station selection.
- Station-wise source identification analysis.
- Potential pollution category indicators.
- Pollutant anomaly analysis.
- Historical pollution behaviour.
- Policy-related information retrieval.
- Evidence-supported recommendations and insights.

### 4.3 Air Quality Monitoring

- Integration of available air quality data sources.
- Storage of historical monitoring records in PostgreSQL.
- Monitoring station-wise AQI and pollutant information.
- Interactive geographical visualization.
- Retrieval of the latest available station readings.

### 4.4 AQI Forecasting

- Trained LightGBM regression model.
- Historical AQI and pollutant information used as model inputs.
- Time-based and environmental input features.
- Forecast generation for the supported prediction horizon.
- Comparison of predicted values with historical observations.

### 4.5 Pollution Source Identification

The system uses a research-guided heuristic methodology to identify potential pollution source categories.

The analysis considers pollutant-specific behaviour and deviations from historical station-level baselines.

The source categories considered include:

- Traffic / Transportation
- Road Dust
- Construction
- Industrial Emissions

The methodology provides relative anomaly-based indicators. It does not claim to calculate exact source-wise emission contribution percentages.

### 4.6 RAG-Based Advisory and Policy Support

Retrieval-Augmented Generation is used to retrieve relevant information from a prepared knowledge base before generating contextual responses.

The platform includes two application-oriented uses:

- **Citizen Health Advisory:** Provides health-related guidance based on air quality conditions and retrieved reference information.
- **Policy Decision Support:** Retrieves relevant policy documents, standards, environmental information, and recommendations to assist policymakers.

---

## 5. System Architecture

The platform follows a modular full-stack architecture consisting of the frontend, backend, database, machine learning components, external data sources, and knowledge retrieval modules.

### High-Level Architecture

```text
                  EXTERNAL DATA SOURCES
                           |
          +----------------+----------------+
          |                |                |
      Air Quality        Weather        Reference &
        Data              Data          Policy Data
          |                |                |
          +----------------+----------------+
                           |
                           v
                 DATA INGESTION LAYER
                           |
                           v
                  FASTAPI BACKEND
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     PostgreSQL       ML FORECASTING     SOURCE
       (Neon)           MODULE          IDENTIFICATION
          |                |                |
          +----------------+----------------+
                           |
                           v
                   ANALYTICAL SERVICES
                           |
             +-------------+-------------+
             |                           |
             v                           v
        HEALTH ADVISORY             POLICY RAG
             |                           |
             +-------------+-------------+
                           |
                           v
                    REACT FRONTEND
                           |
              +------------+------------+
              |                         |
              v                         v
         CITIZEN PORTAL           POLICY MAKER
                                      PORTAL
```

### Architecture Components

| Component | Responsibility |
|---|---|
| React Frontend | User interface, dashboards, maps, charts, and interaction |
| FastAPI Backend | API endpoints, business logic, and integration of services |
| Neon PostgreSQL | Storage of air quality monitoring records and application data |
| Data Ingestion | Collection and storage of air quality information |
| Forecasting Module | AQI prediction using the trained LightGBM model |
| Source Identification | Research-guided pollutant anomaly and source-category analysis |
| RAG Module | Retrieval of relevant health and policy information |
| Authentication | Authentication and access control for policymakers |

---

## 6. Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React.js, JavaScript, HTML, CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL, Neon |
| Machine Learning | LightGBM, Scikit-learn, Pandas, NumPy |
| Data Processing | Python, Pandas, NumPy |
| Geospatial Visualization | Interactive maps and station coordinates |
| Data Sources | Google Air Quality API, Open-Meteo, and available reference datasets |
| AI / Knowledge Retrieval | Retrieval-Augmented Generation (RAG), vector-based retrieval |
| API Communication | REST APIs |
| Version Control | Git and GitHub |
| Automation | GitHub Actions |

---

## 7. Data Sources

The system integrates environmental information from multiple sources.

| Data Source | Purpose |
|---|---|
| CPCB / MPCB | Air quality monitoring information and reference data |
| Google Air Quality API | Location-based air quality information and historical data where supported |
| Open-Meteo | Weather information such as temperature, humidity, and wind conditions |
| Neon PostgreSQL | Storage of collected air quality records |
| MPCB Source Apportionment Report | Research reference for pollution source categories |
| Policy and Government Documents | Knowledge base for policy-related retrieval |
| Health Reference Documents | Knowledge base for citizen health advisories |

The availability, coverage, and update frequency of individual datasets depend on the corresponding data provider.

---

## 8. Database Design

The application uses PostgreSQL hosted on Neon for storing air quality monitoring data.

### Main Table: `air_quality_data`

| Column | Description |
|---|---|
| id | Unique record identifier |
| station_id | Monitoring station identifier |
| station_name | Monitoring station name |
| latitude | Station latitude |
| longitude | Station longitude |
| timestamp | Timestamp of the air quality record |
| aqi | Air Quality Index |
| aqi_category | AQI category |
| pm25 | PM2.5 concentration |
| pm10 | PM10 concentration |
| no2 | Nitrogen dioxide concentration |
| so2 | Sulphur dioxide concentration |
| co | Carbon monoxide concentration |
| o3 | Ozone concentration |
| source | Data source |
| created_at | Record insertion timestamp |

The database supports historical retrieval, station-wise analysis, trend generation, and forecasting-related operations.

Additional application tables are used for the corresponding authentication and application workflows.

---

## 9. Machine Learning: AQI Forecasting

### 9.1 Objective

The forecasting module predicts future AQI values using historical air quality information and engineered input features.

The purpose is to provide an indication of possible future air quality conditions rather than relying only on current readings.

### 9.2 Dataset

The forecasting work uses a historical air quality dataset containing approximately:

- 33,799 observations.
- 20 monitoring stations.
- Historical records covering 26 June 2019 to 16 February 2026.

The dataset undergoes preprocessing and preparation before model training.

### 9.3 Data Preprocessing

The major preprocessing operations include:

1. Handling missing values.
2. Removing or treating invalid and extreme observations.
3. Preparing timestamp-based features.
4. Organizing records chronologically.
5. Preparing the input features required by the forecasting model.
6. Splitting the dataset chronologically into training and testing sets.

An 80:20 chronological split is used to preserve the time order of observations and avoid randomly mixing future records into the training data.

### 9.4 Model Selection

Different machine learning approaches were evaluated during model development.

LightGBM was selected for the implemented forecasting module based on the model evaluation and comparison process.

The final model uses a single AQI lag feature along with other engineered input features.

### 9.5 Model Evaluation

The final reported evaluation metrics are:

| Metric | Value |
|---|---:|
| MAE | 7.4715 |
| RMSE | 11.8617 |
| R² Score | 0.9832 |

**MAE (Mean Absolute Error):** Measures the average absolute difference between actual and predicted values.

**RMSE (Root Mean Squared Error):** Measures prediction error while giving greater weight to larger errors.

**R² Score:** Indicates how well the model explains variation in the target variable on the evaluation dataset.

These results represent the model's performance on the prepared test dataset and should not be interpreted as a guarantee of future real-world accuracy.

---

## 10. Pollution Source Identification Methodology

### 10.1 Objective

The source identification module attempts to identify pollution categories that may be associated with unusual pollutant behaviour at a monitoring station.

Instead of directly estimating source contribution percentages, the system compares current pollutant concentrations against historical station-specific behaviour.

### 10.2 Methodology

The system uses a rolling 30-day historical baseline for each monitoring station.

For each pollutant indicator:

1. Historical readings are retrieved for the selected station.
2. The median concentration is calculated.
3. The Median Absolute Deviation (MAD) is calculated.
4. The current concentration is compared with the historical baseline.
5. A normalized anomaly score is generated.
6. Related pollutant indicators are grouped into source categories.

### 10.3 Anomaly Calculation

The normalized anomaly score is calculated using:

```text
Z = (C - M) / (1.4826 × MAD)
```

Where:

- C = Current pollutant concentration
- M = Historical median concentration
- MAD = Median Absolute Deviation
- 1.4826 = Scaling constant used to make MAD comparable to standard deviation under a normal distribution

The resulting score is clipped to the range -3 to +3 and normalized to obtain a signed indicator between -1 and +1.

```text
Normalized Score = clip(Z, -3, 3) / 3
```

### 10.4 Pollutant-to-Source Association

| Source Category | Associated Indicators |
|---|---|
| Traffic / Transportation | NO2 and CO |
| Road Dust | PM10 and coarse particulate fraction |
| Construction | PM10 and coarse particulate fraction |
| Industrial Emissions | SO2 |

The coarse particulate fraction is estimated as:

```text
Coarse Fraction = max(0, PM10 - PM2.5)
```

Ozone (O3) is treated as contextual information rather than a direct indicator of a single emission source.

### 10.5 Score Interpretation

| Score Behaviour | Interpretation |
|---|---|
| Positive score | Pollutant concentration is above its historical baseline |
| Near-zero score | Pollutant concentration is close to its historical baseline |
| Negative score | Pollutant concentration is below its historical baseline |

The category-level score is derived from the available associated pollutant indicators.

### 10.6 Research Basis

The source categories and pollutant associations are guided by the *Final Report: Air Quality Assessment, Emission Inventory & Source Apportionment Study for Mumbai City* published by MPCB in December 2023.

The research findings provide a reference for selecting relevant source categories and associated pollutants.

### 10.7 Important Methodological Limitation

The module is a research-guided heuristic source identification system, not a chemical source apportionment model.

It does not use chemically speciated particulate samples or a receptor model such as Positive Matrix Factorization (PMF) to calculate exact source contribution percentages.

Meteorological conditions such as wind speed, rainfall, humidity, and atmospheric mixing can also influence pollutant concentrations. The current 30-day median baseline does not fully remove these effects.

Therefore, the displayed results should be interpreted as relative pollutant anomaly indicators and potential source associations, not definitive proof of emission sources or their exact contributions.

---

## 11. Retrieval-Augmented Generation (RAG)

### 11.1 Overview

Retrieval-Augmented Generation combines information retrieval with language-model-based response generation.

Instead of generating responses only from the language model's existing knowledge, the system first retrieves relevant information from a prepared knowledge base.

### 11.2 Citizen Health Advisory

The citizen advisory module uses air quality information and retrieved health-related references to provide contextual guidance.

The workflow is:

```text
Current Air Quality Information
             |
             v
       Advisory Request
             |
             v
     Knowledge Base Retrieval
             |
             v
   Relevant Health Information
             |
             v
       Response Generation
             |
             v
      Citizen Health Advisory
```

### 11.3 Policy Decision Support

The policy RAG module retrieves relevant environmental and policy information to support decision-making.

The knowledge base contains relevant material such as:

- Air quality standards and AQI information.
- Government policy documents.
- Pollution-control guidelines.
- Mumbai-specific environmental information.
- Health and environmental impact references.
- Relevant recommendations and intervention information.

The workflow is:

```text
Selected Monitoring Station
             |
             v
     Source / AQI Analysis
             |
             v
       Policy Query
             |
             v
     Knowledge Base Retrieval
             |
             v
   Relevant Policy Evidence
             |
             v
   Policy Insight / Recommendation
```

RAG outputs are intended to assist users with relevant information. They should be reviewed before being treated as official policy decisions.

---

## 12. Project Workflow

The overall working process of VayuSuchak is as follows:

1. Air quality and environmental information is collected from available data sources.
2. Data is processed and stored in the PostgreSQL database.
3. The backend exposes APIs for accessing air quality information and analytical results.
4. The React frontend retrieves and displays the required information.
5. The forecasting module generates future AQI predictions.
6. The source identification module compares pollutant readings against historical station-specific baselines.
7. Historical trends and station information are displayed through charts and maps.
8. The citizen portal retrieves relevant health information to generate advisories.
9. The policymaker portal retrieves policy-related evidence and presents relevant insights.
10. Users interact with the dashboard to understand air quality conditions and support informed decisions.

---

## 13. Installation and Setup

### 13.1 Prerequisites

Install the following software before running the project:

- Python 3.12
- Node.js and npm
- Git
- Visual Studio Code or another code editor
- PostgreSQL database through Neon
- Required API credentials

### 13.2 Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER
```

Replace the repository URL and folder name with the actual values.

### 13.3 Backend Setup

Open a terminal and navigate to the backend directory:

```powershell
cd backend
```

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\activate
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

Configure the environment variables required by the backend.

Create a `.env` file in the backend directory if that is where the application's configuration loader expects it.

Example:

```env
DATABASE_URL=your_neon_postgresql_connection_string
GOOGLE_AIR_QUALITY_API_KEY=your_google_air_quality_api_key
```

> Add any other environment variables required by the current backend configuration. Never commit API keys, database credentials, passwords, or invitation codes to GitHub.

Start the FastAPI backend:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 13.4 Frontend Setup

Open a separate terminal and navigate to the frontend directory:

```powershell
cd frontend
```

Install the dependencies:

```powershell
npm install
```

Start the React development server:

```powershell
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

### 13.5 Database Setup

1. Create a PostgreSQL project using Neon.
2. Open the SQL Editor in the Neon dashboard.
3. Execute the database table creation scripts supplied with the project.
4. Copy the PostgreSQL connection string.
5. Configure the `DATABASE_URL` environment variable.
6. Verify that the backend can connect to the database.

The database schema and initialization scripts included in the repository should be used as the source of truth for setting up all application tables.

---

## 14. Running the Complete Application

For local demonstration, two separate terminals are required.

**Terminal 1 – Backend**

```powershell
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 – Frontend**

```powershell
cd frontend
npm run dev
```

Open the frontend in a browser:

```text
http://localhost:5173
```

Ensure that the database is accessible and the required environment variables are configured before starting the application.

---

## 15. Project Demonstration Guide

The following sequence can be followed during the final project demonstration.

### Step 1: Introduction

- Introduce VayuSuchak and its objective.
- Explain the problem of fragmented air quality information.
- Describe how the system combines monitoring, forecasting, source identification, and decision support.

### Step 2: Citizen Portal

- Open the application.
- Navigate to the citizen dashboard.
- Allow browser location access when prompted.
- Show the location-based AQI information.
- Explain the AQI category and pollutant values.

### Step 3: Monitoring Station Map

- Open the interactive monitoring station map.
- Show the selected monitoring stations across Mumbai.
- Explain how station locations and air quality information are visualized.
- Select a station to examine its information.

### Step 4: AQI Forecasting

- Open the forecasting section.
- Show the predicted AQI values.
- Explain the LightGBM model and its input features.
- Briefly discuss the chronological training and testing process.
- Present the model evaluation metrics: MAE, RMSE, and R².

### Step 5: Historical Trends

- Open the trends section.
- Demonstrate the available historical time ranges.
- Show AQI and pollutant trends.
- Explain how historical records help identify changes in pollution behaviour.

### Step 6: Health Advisory

- Open the citizen health advisory section.
- Demonstrate the advisory generation process.
- Explain how relevant health information is retrieved from the knowledge base.
- Show how the response provides contextual guidance based on air quality.

### Step 7: Policy Maker Authentication

- Navigate to the policymaker portal.
- Demonstrate the authorized policymaker login.
- If registration is enabled, explain the invitation-code-based registration process.
- Show the protected policymaker interface.

### Step 8: Source Identification

- Open the Source Analysis section.
- Select a monitoring station.
- Display the pollutant anomaly indicators.
- Explain the 30-day historical median and MAD-based methodology.
- Describe the association between pollutant indicators and potential pollution categories.
- Clarify that the results represent relative anomaly-based indicators rather than exact source contribution percentages.

### Step 9: Policy Insights

- Open the Policy Insights section.
- Demonstrate retrieval of relevant policy evidence.
- Show the generated insights and recommendations.
- Explain how the knowledge base supports the policymaker's analysis.

### Step 10: Conclusion

Conclude by explaining how VayuSuchak integrates air quality monitoring, machine learning forecasting, pollution source identification, and RAG-based decision support into one platform.

---

## 16. Expected Outcomes

The proposed system provides:

- A unified interface for accessing air quality information.
- Improved visibility into monitoring station conditions.
- Forecast-based awareness of possible future AQI changes.
- Identification of unusual pollutant behaviour and potential pollution categories.
- Better understanding of historical air quality trends.
- Accessible health-related guidance for citizens.
- Organized environmental and policy information for policymakers.

The system aims to support informed environmental awareness and decision-making through integrated data and analytical services.

---

## 17. Limitations

The current implementation has certain limitations:

1. Forecast accuracy depends on the availability, quality, and representativeness of historical data.
2. Source identification is based on pollutant associations and historical anomaly scores, not direct chemical source apportionment.
3. Meteorological variations can influence pollutant concentrations and are not fully normalized in the current source identification methodology.
4. External API availability, usage limits, and data coverage may affect the availability of live information.
5. RAG-generated responses depend on the quality, relevance, and coverage of the documents in the knowledge base.
6. The system is designed as a decision-support platform and does not replace official pollution-control authorities or regulatory procedures.

---

## 18. Future Scope

The project can be enhanced through the following extensions:

- Integration of additional real-time monitoring stations and IoT sensors.
- Weather-normalized source identification using meteorological variables.
- Integration of satellite-based pollution observations and fire hotspot information.
- Advanced source apportionment using chemically speciated pollutant measurements.
- Improved forecasting through additional model architectures and external environmental features.
- Multilingual health advisories.
- Automated alert and notification mechanisms.
- Persistent storage of policymaker analysis and test results.
- Expanded policy knowledge base with more government documents and updated regulations.
- Additional integrations and workflow automation for environmental monitoring and governance.

---

## 19. Conclusion

VayuSuchak presents an integrated AI-driven approach to urban air quality monitoring and decision support, with a focus on Mumbai. The platform combines environmental data collection, interactive visualization, machine learning-based AQI forecasting, research-guided pollution source identification, and Retrieval-Augmented Generation to address the limitations of conventional air quality monitoring applications.

By providing separate interfaces for citizens and policymakers, the system makes air quality information more accessible while offering analytical support for understanding pollution trends and potential source categories. The forecasting module provides insights into possible future AQI conditions, while the source identification and RAG modules help organize environmental evidence and relevant recommendations.

Overall, VayuSuchak demonstrates how artificial intelligence, data analytics, and knowledge retrieval can be integrated into a unified platform to support environmental awareness and informed decision-making.

---

## 20. Project Information

| Field | Details |
|---|---|
| Project Title | AI-Driven Pollution Source Identification, Forecasting & Policy Decision Support Dashboard for Mumbai |
| Project Name | VayuSuchak |
| Project Type | Final Year Engineering Project |
| Degree | Bachelor of Engineering |
| Department | Computer Engineering |
| Institution | Vivekanand Education Society's Institute of Technology (VESIT) |
| Academic Year | 2026–2027 |
| Domain | Artificial Intelligence, Machine Learning, Big Data, Environmental Monitoring |
| Frontend | React.js |
| Backend | FastAPI |
| Database | PostgreSQL (Neon) |
| Forecasting Model | LightGBM |
| Version Control | GitHub |

### Project Team

Add the names and details of all team members below:

| Sr. No. | Team Member | Class/Roll no |
|---|---|---|
| 1 | Madhura Walawalkar | D17A/63 |
| 2 | Jaee Sakharkar | D17A/52 |
| 3 | Sanskruti Ukarande | D17A/62 |


### Project Guide

**Project Guide:** Mrs. Rupali Soni

**Department:** Computer Engineering

**Institution:** Vivekanand Education Society's Institute of Technology (VESIT)

---

## 21. References

1. Central Pollution Control Board (CPCB) – https://cpcb.nic.in/
2. Maharashtra Pollution Control Board (MPCB) – https://mpcb.gov.in/
3. Google Maps Platform – Air Quality API – https://developers.google.com/maps/documentation/air-quality
4. Open-Meteo – https://open-meteo.com/
5. Neon – Serverless PostgreSQL – https://neon.tech/
6. FastAPI Documentation – https://fastapi.tiangolo.com/
7. React Documentation – https://react.dev/
8. LightGBM Documentation – https://lightgbm.readthedocs.io/
9. MPCB, *Final Report: Air Quality Assessment, Emission Inventory & Source Apportionment Study for Mumbai City*, December 2023.
10. Relevant research papers, environmental standards, government reports, and reference documents used during project development.

---

<p align="center">
  <b>VayuSuchak – Making Air Quality Information More Accessible, Predictive, and Actionable.</b>
</p>
