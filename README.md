# CODGuard AI – Intelligent COD Order Risk & RTO Reduction System

CODGuard AI is an AI-assisted decision support system designed for D2C e-commerce businesses to identify Cash on Delivery (COD) orders with a higher Return to Origin (RTO) risk.

The system combines Machine Learning, a locally running Large Language Model (LLM), configurable business rules, a simulated WhatsApp confirmation workflow, and a Streamlit dashboard.

Its goal is to reduce avoidable RTO costs while protecting genuine customer orders.

## Business Problem

The sample business has:
- 3,000 monthly orders
- 55% COD orders
- Approximately 28% COD RTO rate
- ₹649 average order value

An RTO creates forward shipping, return shipping, packaging, and potential product-damage costs.

CODGuard AI estimates order risk and recommends an appropriate action before shipment.

## Key Features

### 1. Data Analysis
- Historical order data cleaning and preprocessing
- Duplicate removal
- RTO rate analysis
- Analysis by state, courier, marketing source, and customer history

### 2. Machine Learning Prediction
- Logistic Regression
- Random Forest comparison
- RTO probability prediction
- Model evaluation using precision, recall, F1-score, ROC-AUC, and Brier score

### 3. LLM-Based Customer Detail Validation
- Uses Ollama with Qwen2.5:3b
- Examines customer name and address quality
- Identifies potentially incomplete or unclear details
- Returns structured JSON output
- Runs locally without per-request cloud API charges

### 4. Intelligent Decision Engine

The decision engine recommends four possible actions:

| Action | Purpose |
|---|---|
| Ship as-is | Low predicted risk |
| WhatsApp confirmation | Request customer confirmation |
| Prepaid nudge | Encourage online payment |
| Hold for review | Request manual verification |

Risk thresholds are configurable through `backend/config.json`.

The prototype does not automatically cancel orders based only on ML predictions.

### 5. WhatsApp Workflow Simulation
- English, Hinglish, and Kannada message templates
- Order confirmation messages
- Prepaid discount message
- YES, NO, unclear, and no-response scenarios
- Manual review after 24 hours without a response

This is a simulation and is not connected to a live WhatsApp Business API.

### 6. Founder Dashboard
- Historical order summary
- Actual RTO rate
- Predicted risk distribution
- Decision action distribution
- Financial impact scenario analysis
- Estimated RTO savings and potential lost gross profit

Financial impact figures are estimates based on configurable assumptions, not realized savings.

## Technology Stack

- **Language:** Python
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** Scikit-learn
- **LLM:** Ollama – Qwen2.5:3b
- **Backend:** FastAPI components installed; decision workflow currently runs locally
- **Dashboard:** Streamlit
- **Model Storage:** Joblib
- **Visualization:** Matplotlib, Seaborn

## Project Structure

```text
CODGuard-AI/
│
├── backend/
│   ├── analysis/
│   │   ├── data_analysis.py
│   │   ├── eda_analysis.py
│   │   ├── train_model.py
│   │   ├── predict_order.py
│   │   ├── llm_validator.py
│   │   ├── decision_engine.py
│   │   ├── whatsapp_simulator.py
│   │   └── run_codguard.py
│   │
│   ├── data/
│   │   └── orders_sample.csv
│   ├── models/
│   │   └── codguard_model.pkl
│   ├── config.json
│   └── requirements.txt
│
├── dashboard/
│   └── app.py
│
├── docs/
│   ├── business_memo.md
│   ├── decision_log.csv
│   └── ai_usage_log.md
│
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Ollama installed
- Qwen2.5:3b model downloaded

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CODGuard-AI
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv backend/venv
backend\venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Start Ollama

Make sure Ollama is running, then execute:

```bash
ollama run qwen2.5:3b
```

The LLM validator expects Ollama at:

```text
http://localhost:11434
```

### 5. Run the decision workflow

From the project root:

```bash
python backend/analysis/run_codguard.py
```

### 6. Run the founder dashboard

```bash
python -m streamlit run dashboard/app.py
```

Open the local address displayed in the terminal, usually:

```text
http://localhost:8501
```

## Model Evaluation

The initial model evaluation selected Logistic Regression as the candidate model based on its ROC-AUC and related evaluation metrics.

The model achieved:
- ROC-AUC: 0.6727
- RTO precision: 0.4370
- RTO recall: 0.5221
- RTO F1-score: 0.4758

These are initial results from a single train/test split. Further validation, probability calibration, and monitoring are required before production use.

## Business Documentation

See the `docs/` folder for:
- Business recommendation memo
- Sample decision log
- AI usage log

## Limitations and Future Improvements

- Integrate with Shopify order APIs.
- Connect to the official WhatsApp Business API.
- Add time-based model validation and probability calibration.
- Improve address validation and customer-response handling.
- Monitor model performance and decision outcomes.
- Add authentication and role-based dashboard access.
- Deploy the application to a cloud environment.

## Responsible AI

CODGuard AI is a decision-support prototype. High-risk orders are routed for manual review instead of automatic cancellation. Historical correlations and model predictions should not be treated as proof that an individual customer will return an order.

## Author

Developed as an Associate Software Engineer take-home assignment.
