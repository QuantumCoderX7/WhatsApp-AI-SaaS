from typing import List, Dict, Any

GEMINI_TOOLS_DECLARATION: List[Dict[str, Any]] = [
    {
        "name": "check_inventory",
        "description": "Checks the real-time stock quantity available for a specific product SKU.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "sku": {
                    "type": "STRING",
                    "description": "The exact SKU code of the product (e.g. PROD-001)"
                }
            },
            "required": ["sku"]
        }
    },
    {
        "name": "reserve_inventory",
        "description": "Temporarily reserves stock of an item for a customer before completing checkout.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "sku": {
                    "type": "STRING",
                    "description": "Product SKU code"
                },
                "quantity": {
                    "type": "INTEGER",
                    "description": "Number of units to reserve"
                }
            },
            "required": ["sku", "quantity"]
        }
    },
    {
        "name": "search_knowledge",
        "description": "Searches company FAQs, policies, user manuals, and documentation.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The search query keywords or question to look up"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_order",
        "description": "Creates a new pending order for the customer.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "sku": {
                    "type": "STRING",
                    "description": "Product SKU code to purchase"
                },
                "quantity": {
                    "type": "INTEGER",
                    "description": "Quantity to order"
                }
            },
            "required": ["sku", "quantity"]
        }
    },
    {
        "name": "handoff_human",
        "description": "Escalates the WhatsApp chat to a human customer support agent when the customer requests a human or is dissatisfied.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "reason": {
                    "type": "STRING",
                    "description": "Summary explanation of why human escalation was triggered"
                }
            },
            "required": ["reason"]
        }
    }
]
