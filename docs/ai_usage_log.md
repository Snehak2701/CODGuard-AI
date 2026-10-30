# CODGuard AI – AI Usage Log

## 1. Purpose

AI was used in CODGuard AI to assist with customer-detail validation and development support. The project combines machine learning, rule-based business logic, and a locally running Large Language Model (LLM).

## 2. Tools and Technologies Used

| Tool | Purpose |
|---|---|
| Python | Backend development and data processing |
| Pandas and NumPy | Data cleaning and analysis |
| Scikit-learn | RTO prediction model training |
| Ollama – Qwen2.5:3b | Local customer name and address validation |
| Streamlit | Founder dashboard |
| ChatGPT | Development guidance, debugging, code explanations, and documentation support |

## 3. Machine Learning Usage

A Logistic Regression model and a Random Forest model were trained to estimate the probability of an order becoming an RTO.

The models used historical order information such as:
- Order value
- Customer's previous order count
- Customer's previous RTO count
- State and city
- Courier
- Marketing source

The models were compared using classification metrics, including precision, recall, F1-score, ROC-AUC, and Brier score.

Logistic Regression was selected as the initial candidate based on its ROC-AUC and other evaluation results.

## 4. LLM Usage

Ollama with Qwen2.5:3b was used locally to examine customer names and delivery addresses.

The LLM returns structured JSON containing:
- Name quality
- Address quality
- Detected language
- Normalized address
- Potential concerns
- Whether clarification is needed

The LLM is used as an assistive validation layer. It cannot independently verify whether an address physically exists or whether a customer will accept an order.

## 5. Decision Engine

The decision engine combines the predicted RTO probability, customer-detail validation, and configurable business rules.

Possible actions:
- Ship as-is
- Request WhatsApp confirmation
- Nudge the customer to pay online
- Hold for manual review

The system does not automatically cancel an order solely because of its predicted RTO risk.

## 6. WhatsApp Simulation

A simulated WhatsApp workflow was developed to demonstrate:
- Order confirmation messages
- Prepaid payment nudges
- English, Hinglish, and Kannada message templates
- YES, NO, unclear, and no-response scenarios
- Manual review after 24 hours without a response

This is a prototype simulation and is not connected to a live WhatsApp Business API.

## 7. Human Review and Validation

AI-generated outputs are treated as recommendations, not guaranteed facts.

Human review is required for:
- Incomplete or unclear customer details
- High-risk orders
- Cancellation requests
- Uncertain LLM responses

The historical dataset and model evaluation results were reviewed before defining the initial decision thresholds.

## 8. Privacy and Security

- Customer phone numbers and order IDs are not sent to the local LLM.
- Qwen2.5:3b runs locally through Ollama.
- API keys and credentials should not be committed to the GitHub repository.
- The project should use synthetic or appropriately anonymized customer data for public demonstrations.

## 9. Limitations

- The model is trained on a relatively small historical dataset.
- The current evaluation uses a single train/test split.
- Predicted probabilities have not yet been calibrated.
- Historical correlations do not establish causation.
- The WhatsApp workflow is simulated, not a live integration.
- The dashboard uses a historical dataset rather than live Shopify orders.

## 10. Responsible AI Approach

CODGuard AI uses AI to support operational decisions while keeping final high-impact decisions under human control. The system is designed to reduce avoidable RTO costs without unfairly rejecting genuine customers.
## 11. Examples of Weak AI Outputs and Corrections

### Example 1: Inconsistent address validation
- **Tool:** Ollama – Qwen2.5:3b.
- **Weak output:** The LLM classified the same address differently across separate test runs, sometimes marking it COMPLETE and sometimes INCOMPLETE.
- **How it was caught:** The output was tested more than once and the classifications were compared.
- **Correction:** LLM validation was treated as an assistive signal rather than a final decision. Unclear or incomplete details are routed for manual review.

### Example 2: Missing address information
- **Tool:** Ollama – Qwen2.5:3b.
- **Weak output:** During an early test, the LLM returned an address assessment without identifying all expected address components, including the postal code.
- **How it was caught:** The generated JSON was inspected against the original customer address.
- **Correction:** The output structure was made more explicit, and the application uses a safe fallback when the LLM response is incomplete or invalid. Physical address verification remains outside the LLM's capabilities.

### Example 3: Model probability interpretation
- **Tool:** Machine learning model and AI-assisted development.
- **Potentially misleading interpretation:** A high predicted RTO probability could be mistaken for certainty that an individual order will become an RTO.
- **How it was caught:** Test-set evaluation showed limited model performance, with ROC-AUC of 0.6727 and RTO precision of 0.4370.
- **Correction:** Predictions are presented as risk estimates, not guaranteed outcomes. High-risk orders are held for human review, and automatic cancellation based solely on model predictions is disabled.

