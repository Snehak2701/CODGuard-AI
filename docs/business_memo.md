# CODGuard AI – Business Recommendation Memo

**To:** Founder, D2C Haircare Brand  
**From:** CODGuard AI Project Team  
**Date:** 31 October 2026  
**Subject:** Reducing Cash-on-Delivery Returns to Origin (RTO)

## 1. Executive Summary

The business currently faces a significant Cash-on-Delivery (COD) return problem. COD orders have an approximate RTO rate of 28%, compared with approximately 4% for prepaid orders.

CODGuard AI is a data-driven decision support system designed to identify potentially risky COD orders before shipment. It combines a machine learning model for RTO risk prediction, a locally hosted Large Language Model (LLM) for customer name and address quality checks, and configurable business rules.

The system recommends four actions: Ship As-Is, WhatsApp Confirmation, Prepaid Nudge, and Hold for Manual Review.

**Recommendation:** Introduce CODGuard AI through a controlled pilot. Prioritize customer confirmation and prepaid conversion instead of automatically cancelling high-risk orders.

## 2. Key Findings from Historical Order Data

The supplied dataset contained 2,018 records. After removing 30 exact duplicate records and excluding one in-transit order, 1,987 completed orders were available for analysis.

**Finding 1 – Significant RTO rate**

- Delivered orders: 1,422.
- RTO orders: 565.
- Actual RTO rate: 28.43%.

This indicates a substantial opportunity to reduce avoidable COD-related logistics costs.

**Finding 2 – Previous RTO history is an important risk indicator**

| Previous RTO count | Orders | RTO rate |
|---|---:|---:|
| 0 | 1,845 | 27.15% |
| 1 | 108 | 35.19% |
| 2 | 34 | 76.47% |

Customers with two previous RTOs showed a much higher historical RTO rate. However, this group contains only 34 orders, so the result should be treated cautiously.

**Finding 3 – RTO rates vary across marketing channels**

| Marketing source | Orders | RTO rate |
|---|---:|---:|
| Meta Ads | 765 | 31.24% |
| Instagram Organic | 232 | 29.31% |
| Google Ads | 244 | 28.28% |
| Direct | 253 | 22.92% |

Meta Ads has the highest RTO rate among these channels, while Direct has the lowest. Marketing source should be monitored as a risk signal, not used as an independent reason to reject orders.

These are historical associations, not proof of causation. State, courier, campaign and customer differences may influence the results.

## 3. Recommended Decision Rules

The prototype uses the following configurable initial thresholds:

| Predicted RTO risk | Recommended action |
|---|---|
| Below 20% | Ship As-Is |
| 20% to below 40% | WhatsApp Confirmation |
| 40% to below 65% | Prepaid Nudge |
| 65% and above | Hold for Manual Review |

Additional rules:

- Incomplete addresses should be verified before shipment.
- Suspicious or unclear customer details should trigger verification.
- A YES response should confirm customer intent.
- A NO response should create a cancellation request for review.
- An unclear response should trigger a clarification message.
- No response after 24 hours should lead to manual review.
- High ML risk alone must never trigger automatic cancellation.

These thresholds are starting assumptions. They must be evaluated against actual intervention outcomes before production deployment.

## 4. Financial Impact and Operations vs Marketing Trade-off

The assignment provides the following financial assumptions:

| Metric | Amount |
|---|---:|
| Average order value | ₹649 |
| Delivered gross profit per order (62%) | ₹402.38 |
| Forward shipping | ₹65 |
| Return shipping | ₹65 |
| Packaging and handling | ₹25 |
| Expected damage cost | ₹14.40 |
| Direct expected cost per RTO | ₹169.40 |
| Proposed prepaid discount | ₹20 |

The expected direct RTO cost is ₹169.40 per returned order.

**Operations perspective:** WhatsApp confirmation and manual verification can reduce avoidable RTOs, potentially saving shipping, packaging and damage costs.

**Marketing perspective:** A ₹20 prepaid discount can encourage customers to switch from COD to prepaid. However, discounts reduce contribution margin and should be offered selectively.

The dashboard estimates financial impact using configurable intervention assumptions. These are scenario estimates, not realized savings. Actual results must be measured through customer responses, payment conversion and final delivery outcomes.

The business should compare the cost of prepaid discounts against the expected RTO cost avoided and the gross profit potentially lost from incorrectly rejected genuine orders.

## 5. Risks and Monitoring

Key risks include:

- **False positives:** Genuine customers may be classified as high risk.
- **Model limitations:** The initial model has moderate predictive performance and requires calibration and stronger validation.
- **LLM inconsistency:** Address quality assessments can vary. Deterministic checks and manual verification should support LLM output.
- **Customer experience:** Excessive confirmation messages or aggressive prepaid nudges may reduce conversion.
- **Data privacy:** Customer phone numbers and personally identifiable information must not be unnecessarily shared with the LLM.
- **Operational bias:** State, courier and marketing correlations should not result in blanket rejection policies.

Monitor RTO rate, confirmation response rate, prepaid conversion, false-positive rate, cancellation rate, discount cost and net contribution impact.

## 6. Next Two Weeks

**Week 1 – Validation and Pilot Preparation**

- Review model predictions and validate feature availability at order time.
- Evaluate model calibration and performance using time-based validation.
- Finalize configurable thresholds and customer message templates.
- Test YES, NO, unclear and no-response scenarios.
- Prepare an operational manual-review process.

**Week 2 – Controlled Pilot**

- Run CODGuard on a limited share of eligible COD orders.
- Keep a comparable control group using the existing process.
- Track customer confirmation, prepaid conversion and delivered/RTO outcomes.
- Compare intervention costs, genuine-order losses and RTO savings.
- Review results with Operations and Marketing before expanding.

## 7. Final Recommendation

CODGuard AI should initially operate as a decision-support system, not an automatic order-cancellation system.

A controlled pilot with transparent rules, customer-friendly communication and continuous measurement will help determine whether the system can reduce RTO costs without damaging genuine customer conversions.

**The objective is not simply to reject risky orders. It is to deliver more genuine orders while reducing avoidable business losses.**