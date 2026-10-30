
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"


def validate_customer_details(customer_name, address):

    prompt = f"""
    You are an address and customer name quality validator
    for an Indian COD e-commerce business.

    Analyze the following information:

    Customer Name: {customer_name}
    Address: {address}

    Rules:
    1. Identify suspicious or meaningless customer names.
    2. Check whether the address contains enough information
       for delivery, such as house/flat number, street/locality,
       city and state or PIN code.
    3. Understand Indian English and Hinglish addresses.
    4. Do not mark Hinglish as suspicious.
    5. Never invent missing address details.
    6. Do not claim that an address physically exists.
    7. If uncertain, use UNCLEAR.

    Return ONLY valid JSON in this exact structure:

    {{
        "name_quality": "NORMAL",
        "address_quality": "COMPLETE",
        "language": "English",
        "normalized_address": "",
        "concerns": [],
        "clarification_needed": false,
        "reason": ""
    }}

    Allowed values:
    name_quality: NORMAL, SUSPICIOUS, UNCLEAR
    address_quality: COMPLETE, INCOMPLETE, UNCLEAR
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0
                }
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()
        content = result["message"]["content"]

        validation = json.loads(content)

        required_fields = [
            "name_quality",
            "address_quality",
            "language",
            "normalized_address",
            "concerns",
            "clarification_needed",
            "reason"
        ]

        for field in required_fields:
            if field not in validation:
                raise ValueError(f"Missing field: {field}")

        if validation["name_quality"] not in [
            "NORMAL", "SUSPICIOUS", "UNCLEAR"
        ]:
            raise ValueError("Invalid name_quality")

        if validation["address_quality"] not in [
            "COMPLETE", "INCOMPLETE", "UNCLEAR"
        ]:
            raise ValueError("Invalid address_quality")

        return validation

    except Exception as error:
        print("Ollama validation error:", error)

        return {
            "name_quality": "UNCLEAR",
            "address_quality": "UNCLEAR",
            "language": "Unknown",
            "normalized_address": "",
            "concerns": ["AI validation unavailable"],
            "clarification_needed": True,
            "reason": "Could not validate customer details"
        }


if __name__ == "__main__":

    test_result = validate_customer_details(
        "Priya Sharma",
        "24, 3rd Main, HSR Layout, Bengaluru, Karnataka"
    )

    print("\nCODGuard AI - LLM Validation Result")
    print(json.dumps(test_result, indent=4))
