# CODGuard AI – Decision Log

This document records important technical and business decisions made during development.

### Decision 1: Use machine learning for RTO prediction
- **Alternatives considered:** Fixed business rules only, Logistic Regression, Random Forest.
- **Chosen:** Logistic Regression as the initial candidate.
- **Reason:** It achieved better ROC-AUC (0.6727) than Random Forest (0.6601) on the initial test split.
- **Trade-off:** Random Forest had higher accuracy, but accuracy alone was not the main selection metric.

### Decision 2: Do not automatically cancel high-risk orders
- **Alternatives considered:** Automatically cancel high-risk orders or send them for manual review.
- **Chosen:** Hold high-risk orders for manual review.
- **Reason:** False positives could result in genuine customer orders being rejected.
- **Trade-off:** Manual review requires operational effort but protects customer experience.

### Decision 3: Use an LLM for customer-detail validation
- **Alternatives considered:** Regex-only validation, cloud LLM API, local LLM.
- **Chosen:** Ollama with Qwen2.5:3b.
- **Reason:** Local execution avoids per-request cloud API charges and allows natural-language address assessment.
- **Trade-off:** Local model quality and consistency require human verification.

### Decision 4: Use configurable risk thresholds
- **Alternatives considered:** Hardcoded thresholds or configurable thresholds.
- **Chosen:** Configurable thresholds in `backend/config.json`.
- **Reason:** Business teams can adjust actions without modifying the decision-engine code.
- **Trade-off:** Initial thresholds are prototype assumptions and need validation against actual business outcomes.

### Decision 5: Simulate WhatsApp rather than integrate a live API
- **Alternatives considered:** Live WhatsApp Business API integration or local simulation.
- **Chosen:** Local simulation.
- **Reason:** Demonstrates confirmation, prepaid nudges, customer responses, and 24-hour no-response handling without requiring external API credentials.
- **Trade-off:** Real customer messaging and delivery-status integration remain future work.

### Decision 6: Build the founder dashboard using Streamlit
- **Alternatives considered:** React dashboard or Streamlit.
- **Chosen:** Streamlit.
- **Reason:** Faster implementation of interactive charts and financial scenario analysis using Python.
- **Trade-off:** Less frontend customization than a dedicated React application.

### Decision 7: Keep financial impact as scenario estimates
- **Alternatives considered:** Present estimated savings as actual realized savings or label them as projections.
- **Chosen:** Scenario-based estimates.
- **Reason:** The project uses historical sample data and simulated intervention outcomes, not verified live business results.
- **Trade-off:** Results depend on assumptions such as intervention success and manual cancellation rates.
