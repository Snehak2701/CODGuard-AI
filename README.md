# CODGuard AI – Intelligent COD Order Risk & RTO Reduction System

CODGuard AI is an AI-assisted decision-support system designed for Direct-to-Consumer (D2C) e-commerce businesses to identify Cash-on-Delivery (COD) orders with a higher Return-to-Origin (RTO) risk.

It combines Machine Learning, a locally running Large Language Model (LLM), configurable business rules, a simulated WhatsApp confirmation workflow, and a Streamlit dashboard.

Its goal is to reduce avoidable RTO costs while protecting genuine customer orders.

## 1. Business Problem

The sample business context:

- Monthly orders: 3,000
- COD orders: 55%
- Approximate COD RTO rate: 28%
- Average order value: ₹649

An RTO creates forward shipping, return shipping, packaging, handling, and potential product-damage costs.

CODGuard AI estimates order-level RTO risk and recommends an appropriate action before shipment.

## 2. Key Features

### 2.1 Historical Data Analysis

- Data cleaning and preprocessing
- Duplicate removal
- RTO rate analysis
- Analysis by state, courier, marketing source, order value, and customer history
- September 2026 historical replay

### 2.2 Machine Learning Prediction

- Logistic Regression model
- Random Forest comparison
- RTO probability prediction
- Model evaluation using precision, recall, F1-score, ROC-AUC, and Brier score
- Chronological train/test validation
- Risk-threshold analysis

### 2.3 LLM-Based Customer Detail Validation

- Uses Ollama with Qwen2.5:3b
- Examines customer name and address quality
- Identifies potentially incomplete or unclear details
- Returns structured validation output
- Runs locally without per-request cloud API charges

The LLM assists with data-quality checks. It cannot verify whether an address is physically deliverable.

### 2.4 Intelligent Decision Engine

The decision engine recommends four possible actions:

| Action | Purpose |
|---|---|
| Ship as-is | Low predicted risk |
| WhatsApp confirmation | Request customer confirmation |
| Prepaid nudge | Encourage online payment |
| Hold for review | Request manual verification |

The current configurable risk bands are:

| Predicted RTO risk | Recommended action |
|---|---|
| Below 20% | Ship as-is |
| 20–40% | WhatsApp confirmation |
| 40–60% | Prepaid nudge |
| 60–70% | Manual review |
| 70% and above | Priority manual review |

Risk thresholds and financial assumptions are maintained in `backend/config.json`.

The prototype does not automatically cancel orders based only on ML predictions.

### 2.5 WhatsApp Workflow Simulation

- English, Hinglish, and Kannada message templates
- Order confirmation messages
- Prepaid discount message
- YES, NO, unclear, and no-response scenarios
- Manual review after 24 hours without a response

This is a simulation and is not connected to a live WhatsApp Business API.

### 2.6 Founder Dashboard

The Streamlit dashboard provides:

- Historical order summary
- Actual RTO rate
- Predicted risk distribution
- Decision action distribution
- Financial impact scenario analysis
- Estimated RTO-cost reduction and potential lost contribution

Financial impact figures are estimates based on configurable assumptions, not realised savings.

## 3. Technology Stack

| Area | Technologies |
|---|---|
| Programming language | Python |
| Data analysis | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| LLM | Ollama – Qwen2.5:3b |
| Dashboard | Streamlit |
| Model storage | Joblib |
| Data visualisation | Matplotlib, Seaborn |
| Configuration | JSON |
| Version control | Git, GitHub |

## 4. Project Structure

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
│   │   ├── run_codguard.py
│   │   ├── replay_september.py
│   │   ├── calibration_september.py
│   │   ├── time_based_validation.py
│   │   ├── threshold_analysis.py
│   │   └── intervention_economics.py
│   │
│   ├── data/
│   │   ├── orders_sample.csv
│   │   ├── september_2026_replay.csv
│   │   ├── september_calibration_report.csv
│   │   ├── time_based_test_results.csv
│   │   ├── time_based_calibration.csv
│   │   └── threshold_analysis.csv
│   │
│   ├── models/
│   │   ├── codguard_model.pkl
│   │   └── codguard_time_validated_model.pkl
│   │
│   ├── config.json
│   └── requirements.txt
│
├── dashboard/
│   └── app.py
│
├── docs/
│   ├── business_memo.md
│   ├── CODGuard_AI_Business_Memo.pdf
│   ├── decision_log.csv
│   ├── decision_log.md
│   └── ai_usage_log.md
│
├── .gitignore
└── README.md
```

The structure above lists the main project files. Generated analysis outputs may be added as the project evolves.

## 5. Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Windows, macOS, or Linux
- Ollama and Qwen2.5:3b for the LLM validation workflow

### Step 1: Clone the repository

```bash
git clone https://github.com/Snehak2701/CODGuard-AI.git
cd CODGuard-AI
```

### Step 2: Create a virtual environment

Windows PowerShell:

```powershell
python -m venv backend/venv
```

Activate it:

```powershell
.\backend\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

From the project root:

```bash
pip install -r backend/requirements.txt
```

### Step 4: Run the decision workflow

For the LLM validation component, install Ollama and download Qwen2.5:3b separately.

```bash
ollama pull qwen2.5:3b
```

Start Ollama:

```bash
ollama serve
```

In another terminal, activate the project virtual environment and run:

```bash
python backend/analysis/run_codguard.py
```

The local Ollama service is expected at:

```text
http://localhost:11434
```

### Step 5: Run the dashboard

From the project root:

```bash
python -m streamlit run dashboard/app.py
```

Open the local address displayed in the terminal, usually:

```text
http://localhost:8501
```

**Setup note:** Python installation and dashboard setup can be completed separately from the LLM download. Downloading the Ollama model depends on internet speed and may take additional time.

## 6. Model Evaluation

Two evaluation approaches were used.

### Initial random train/test split

The initial Logistic Regression model achieved:

| Metric | Result |
|---|---:|
| ROC-AUC | 0.6727 |
| RTO precision | 0.4370 |
| RTO recall | 0.5221 |
| F1-score | 0.4758 |

### Chronological time-based validation

A separate model was trained on earlier orders and evaluated on later orders.

| Metric | Result |
|---|---:|
| Training orders | 1,569 |
| Testing orders | 418 |
| Accuracy | 72.25% |
| RTO precision | 41.18% |
| RTO recall | 12.73% |
| F1-score | 19.44% |
| ROC-AUC | 0.6414 |
| Brier score | 0.1851 |

The time-based validation is the more relevant estimate of performance on later orders. Its low RTO recall indicates that many actual RTO orders are missed.

The model is therefore intended for risk prioritisation and controlled experimentation, not automatic order cancellation.

## 7. Financial Analysis and Business Decision

The project uses the following financial assumptions:

- Average order value: ₹649
- Gross margin: 62%
- Forward shipping: ₹65
- Return shipping: ₹65
- Packaging and handling: ₹25
- Product cost: ₹180
- Product damage probability on RTO: 8%

Estimated direct RTO cost:

```text
Forward shipping       ₹65.00
Return shipping        ₹65.00
Packaging and handling ₹25.00
Expected damage cost   ₹14.40
--------------------------------
Total RTO cost         ₹169.40
```

The break-even RTO probability depends on whether forward shipping is already included in gross margin. This assumption must be confirmed with Finance.

The project also evaluates simulated WhatsApp confirmation and prepaid-nudge scenarios. These estimates depend on assumptions about customer response, conversion, and risk reduction. They are not measured savings.

## 8. Business Documentation

The `docs/` folder contains:

- `business_memo.md` – Business findings, financial assumptions, and recommendations.
- `business_memo.pdf` – PDF version of the business memo.
- `decision_log.csv` – Structured decision examples.
- `decision_log.md` – Decision rules and explanations.
- `ai_usage_log.md` – AI usage, errors, and corrections.

## 9. Limitations and Future Improvements

- Integrate with Shopify order APIs.
- Connect to the official WhatsApp Business API.
- Improve probability calibration and model recall.
- Validate interventions using controlled experiments.
- Improve address validation and customer-response handling.
- Monitor model performance and decision outcomes.
- Add authentication and role-based dashboard access.
- Deploy the application to a cloud environment.

## 10. Responsible AI

CODGuard AI is a decision-support prototype.

High-risk orders are routed for manual review instead of automatic cancellation. Historical correlations and model predictions should not be treated as proof that an individual customer will return an order.

The LLM is used for assisting with customer-detail quality checks, not for making financial decisions or verifying physical deliverability.

## Author

Developed as an Associate Software Engineer take-home assignment.