# CODGuard AI — Business Decision Memo

**Subject:** Reducing Cash-on-Delivery Return-to-Origin (RTO) Losses  
**Prepared for:** D2C Haircare Operations and Marketing Teams

## 1. Executive Summary

CODGuard AI is a COD order risk-scoring and decision-support system designed to reduce avoidable Return-to-Origin (RTO) costs. It combines a machine-learning model, address/name validation using a local LLM, configurable business rules, and an intervention decision engine.

The model provides some ability to rank orders by RTO risk, but its time-based validation shows limited recall. It should therefore support prioritisation and manual review—not automatic cancellation.

The recommended pilot uses WhatsApp confirmation, prepaid nudges and manual review, with actual intervention outcomes measured before claiming savings.

## 2. Historical Data Findings

The completed dataset contains **1,987 orders**, after removing 30 exact duplicates and excluding one in-transit record.

- Overall RTO rate: **28.43%** (565 RTOs out of 1,987 completed orders).
- September 2026: **329 completed orders**, including 86 RTOs and 243 delivered orders.
- September RTO rate: **26.14%**.
- Estimated direct September RTO cost: **₹14,568.40**, using ₹169.40 per RTO.

Notable patterns:

- Customers with two previous RTOs had a 76.47% historical RTO rate, based on only 34 orders.
- Orders marked with weak addresses had a 66.39% RTO rate, compared with 25.95% for other orders.
- Meta Ads orders had a 31.24% RTO rate, compared with 22.92% for direct orders.
- Bihar and Uttar Pradesh had higher observed RTO rates than several other states.

These are historical associations, not proof of causation. Small groups and differences in customer mix should be considered before changing marketing or delivery policies.

## 3. Model Performance and Validation

A Logistic Regression pipeline was selected after comparing it with Random Forest.

**Time-based validation:**

| Metric | Result |
|---|---:|
| Training orders | 1,569 |
| Test orders | 418 |
| Accuracy | 72.25% |
| RTO precision | 41.18% |
| RTO recall | 12.73% |
| F1 score | 19.44% |
| ROC-AUC | 0.6414 |
| Brier score | 0.1851 |

The model's Brier score was modestly better than the training-period prevalence baseline of 0.1946. However, ROC-AUC of 0.6414 and recall of 12.73% indicate limited predictive performance at the default 50% threshold. Accuracy was also below the majority-class baseline of 73.68%.

The September calibration check showed an average predicted risk of 46.01%, compared with an actual RTO rate of 26.14%. This indicates overestimation in that period.

**Conclusion:** The model is suitable for experimentation and risk prioritisation, not as a standalone authority for cancelling orders.

## 4. Financial Decision Framework

Assignment-supplied financial assumptions:

- Average order value: ₹649
- Gross margin: 62%, equivalent to ₹402.38 per delivered order
- Forward shipping: ₹65
- Return shipping: ₹65
- Packaging and handling: ₹25
- Product cost: ₹180
- Damage probability on returned products: 8%

Expected product damage cost per RTO is ₹14.40. Therefore:

**Estimated direct RTO cost = ₹65 + ₹65 + ₹25 + ₹14.40 = ₹169.40.**

If the 62% gross margin excludes forward shipping, delivered contribution after forward shipping is ₹337.38. The break-even RTO probability for shipping versus cancelling is approximately **66.57%**.

If the 62% margin already includes forward shipping, delivered contribution is ₹402.38 and the break-even probability is approximately **70.38%**.

Finance must confirm which margin interpretation is correct before production thresholds are approved.

Customer acquisition cost is ₹300 or more, but it is already incurred when the order reaches the decision stage. It should not be subtracted again as an incremental cancellation cost. Potential lost repeat-customer value cannot be quantified without customer lifetime value data.

## 5. Threshold Analysis

The time-based test set was evaluated at different risk thresholds. A flagged order means the model predicted RTO risk at or above that threshold.

| Threshold | Flagged orders | Actual RTOs identified | Genuine delivered orders flagged | RTO recall |
|---|---:|---:|---:|---:|
| 20% | 291 | 88 | 203 | 80.00% |
| 40% | 73 | 32 | 41 | 29.09% |
| 60% | 17 | 11 | 6 | 10.00% |
| 70% | 5 | 4 | 1 | 3.64% |
| 80% | 1 | 1 | 0 | 0.91% |

A historical cancellation counterfactual produced negative estimated net impact at thresholds from 20% through 60%. At 70%, the estimate was positive ₹340.22, but it involved only five flagged orders. At 80%, it involved only one order.

These small samples are insufficient to establish a profitable cancellation policy. The results reinforce the need to avoid automatic cancellation.

## 6. Intervention Economics

The time-based test set was grouped using the current project action bands.

| Action | Orders | Historical RTOs |
|---|---:|---:|
| Ship as-is | 127 | 22 |
| WhatsApp confirmation | 218 | 56 |
| Prepaid nudge | 56 | 21 |
| Hold for review | 17 | 11 |

Using configurable illustrative assumptions:

**WhatsApp confirmation**
- Assumed relative RTO-risk reduction: 30%.
- Baseline expected RTOs: 59.48.
- Expected RTOs after intervention: 41.63.
- Expected RTOs avoided: 17.84.
- Gross estimated RTO-cost reduction: **₹3,022.55**.

WhatsApp service costs are excluded. This is a simulation, not a measured intervention result.

**Prepaid nudge**
- Assumed prepaid conversion: 25%.
- Assumed prepaid RTO probability: 4%.
- Assumed discount: ₹20 per conversion.
- Expected conversions: 14.
- Expected RTOs avoided: 5.99.
- Discount expense: ₹280.
- Estimated net impact: **₹734.42** before payment gateway, messaging and other costs.

Both estimates depend on assumptions that need to be tested with actual customers. Expected RTOs avoided are model-based estimates, not guaranteed prevented returns.

## 7. Recommended Operations and Marketing Pilot

Use the following initial policy as a controlled pilot, subject to Finance and Operations approval:

| Predicted risk | Recommended action |
|---|---|
| Below 20% | Ship as-is |
| 20–40% | WhatsApp confirmation |
| 40–60% | Prepaid nudge |
| 60–70% | Manual review |
| 70% and above | Priority manual review |

Do not automatically cancel orders based only on a model score.

**Operations should:**
- Test WhatsApp confirmation with a recorded YES, NO or no-response outcome.
- Manually review high-risk orders and record the final decision.
- Track actual RTO rates, review workload and service costs.

**Marketing should:**
- Test the prepaid offer and record conversion.
- Track discount expense and payment costs.
- Monitor genuine customer drop-off and avoid penalising first-time customers without sufficient evidence.

## 8. Risks and Next Steps

Key risks include weak model recall, probability calibration drift, small high-risk samples, incomplete address validation, courier or marketing mix changes, and unmeasured intervention effectiveness.

The local LLM should be limited to assisting with address/name quality checks. It should not be treated as proof that an address is deliverable or as a replacement for human review.

**Two-week pilot plan:**

1. **Week 1:** Confirm financial assumptions with Finance, configure thresholds, prepare WhatsApp and prepaid workflows, and establish baseline reporting.
2. **Week 2:** Run a controlled pilot, record intervention responses and outcomes, compare against a suitable control group, and review actual contribution after intervention costs.

### Final Recommendation

Proceed with CODGuard AI as a **human-in-the-loop decision-support pilot**. The historical data indicates meaningful RTO patterns, but current model performance does not justify automatic cancellation. Measure actual WhatsApp and prepaid outcomes before scaling or claiming financial savings.