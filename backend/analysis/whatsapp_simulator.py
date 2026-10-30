
def get_confirmation_message(customer_name, order_id, language="English"):

    if language == "Hinglish":
        message = f"""
Hi {customer_name}! 👋

Thank you for your order #{order_id}.

Aapka order confirm karna hai.
Kya aap is order ko receive karna chahte hain?

Reply YES to confirm.
Reply NO to cancel.

Thank you!
Team CODGuard
"""

    elif language == "Kannada":
        message = f"""
ನಮಸ್ಕಾರ {customer_name}! 👋

ನಿಮ್ಮ ಆರ್ಡರ್ #{order_id} ಗಾಗಿ ಧನ್ಯವಾದಗಳು.

ನೀವು ಈ ಆರ್ಡರ್ ಸ್ವೀಕರಿಸಲು ಬಯಸುವಿರಾ?

YES ಎಂದು ಉತ್ತರಿಸಿ ಆರ್ಡರ್ ಖಚಿತಪಡಿಸಿ.
NO ಎಂದು ಉತ್ತರಿಸಿ ರದ್ದುಗೊಳಿಸಲು ವಿನಂತಿಸಿ.

ಧನ್ಯವಾದಗಳು!
Team CODGuard
"""

    else:
        message = f"""
Hi {customer_name}! 👋

Thank you for your order #{order_id}.

Would you like to confirm this Cash on Delivery order?

Reply YES to confirm.
Reply NO to request cancellation.

Thank you!
Team CODGuard
"""

    return message


def get_prepaid_message(customer_name, order_id, discount):

    return f"""
Hi {customer_name}! 😊

Complete your order #{order_id} with prepaid payment
and get an additional ₹{discount} discount!

Prepaid payment helps us process your order faster.

Would you like to pay online?

Thank you!
Team CODGuard
"""

def process_customer_response(reply, hours_elapsed=0):

    reply = reply.strip().upper()

    # Customer confirms the order
    if reply in ["YES", "Y", "CONFIRM"]:
        return {
            "status": "CONFIRMED",
            "action": "SHIP_ORDER",
            "reason": "Customer confirmed the order."
        }

    # Customer requests cancellation
    elif reply in ["NO", "N", "CANCEL"]:
        return {
            "status": "CANCELLATION_REQUESTED",
            "action": "REVIEW_CANCELLATION",
            "reason": "Customer does not want the order."
        }

    # Customer sends an unclear reply
    elif reply not in ["NO_RESPONSE", ""]:
        return {
            "status": "UNCLEAR_RESPONSE",
            "action": "ASK_FOR_CLARIFICATION",
            "reason": "Customer response was not understood."
        }

    # Customer does not respond within 24 hours
    if hours_elapsed >= 24:
        return {
            "status": "NO_RESPONSE_24H",
            "action": "HOLD_FOR_REVIEW",
            "reason": "Customer did not respond within 24 hours."
        }

    # Still waiting for a response
    return {
        "status": "WAITING",
        "action": "WAIT_FOR_RESPONSE",
        "reason": "Waiting for customer confirmation."
    }


# Test customer responses
if __name__ == "__main__":

    test_replies = [
        ("YES", 1),
        ("NO", 2),
        ("Maybe tomorrow", 3),
        ("NO_RESPONSE", 24),
        ("NO_RESPONSE", 12)
    ]

    print("\n===== CUSTOMER RESPONSE SIMULATION =====")

    for reply, hours in test_replies:

        result = process_customer_response(reply, hours)

        print(f"\nCustomer Reply: {reply}")
        print(f"Hours Elapsed: {hours}")
        print(f"Status: {result['status']}")
        print(f"Action: {result['action']}")
        print(f"Reason: {result['reason']}")


# Test the message templates
if __name__ == "__main__":

    print("===== WHATSAPP CONFIRMATION =====")

    message = get_confirmation_message(
        "Priya Sharma",
        "CG101",
        "English"
    )

    print(message)

    print("\n===== PREPAID OFFER =====")

    prepaid = get_prepaid_message(
        "Priya Sharma",
        "CG101",
        20
    )

    print(prepaid)
