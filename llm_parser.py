import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define the expense extraction tool
expense_tool = genai.protos.Tool(
    function_declarations=[
        genai.protos.FunctionDeclaration(
            name="log_expense",
            description="Extract and log expense information from user message",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "amount": genai.protos.Schema(
                        type=genai.protos.Type.NUMBER,
                        description="The amount of money spent",
                    ),
                    "category": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Category of expense (e.g., food, transport, coffee, groceries, entertainment, shopping, bills, health, other)",
                    ),
                    "description": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Brief description of the expense",
                    ),
                    "needs_clarification": genai.protos.Schema(
                        type=genai.protos.Type.BOOLEAN,
                        description="True if the message is unclear and needs clarification",
                    ),
                    "clarification_question": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Question to ask user if clarification is needed",
                    ),
                },
                required=["amount"],
            ),
        )
    ]
)


def parse_expense_message(user_message: str) -> Dict[str, Any]:
    """Parse expense message using Gemini AI"""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp", tools=[expense_tool]
        )

        system_prompt = """You are an expense tracking assistant. Your job is to extract expense information from user messages.

Rules:
1. Extract the amount, category, and description from natural language
2. Common categories: food, transport, coffee, groceries, entertainment, shopping, bills, health, other
3. If the message doesn't contain an expense or amount, set needs_clarification to true
4. Be smart about context - "coffee 5" means $5 for coffee
5. If currency symbol is present, ignore it (assume user's default currency)
6. For ambiguous messages, ask for clarification

Examples:
- "coffee 5" → amount: 5, category: "coffee", description: "coffee"
- "lunch 23.50 with Sarah" → amount: 23.50, category: "food", description: "lunch with Sarah"  
- "uber to airport 45" → amount: 45, category: "transport", description: "uber to airport"
- "groceries" → needs_clarification: true, clarification_question: "How much did you spend on groceries?"
"""

        full_prompt = f"{system_prompt}\n\nUser message: {user_message}"

        response = model.generate_content(full_prompt)

        # Check if there's a function call
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_call = part.function_call
                    if function_call.name == "log_expense":
                        # Convert args to dict
                        args = dict(function_call.args)
                        return {"success": True, "data": args}

        # If no function call, return the text response
        text_response = response.text if hasattr(response, "text") else None
        return {
            "success": False,
            "message": text_response
            or "I couldn't understand that. Please try something like 'coffee 5' or 'lunch 25.50'",
        }

    except Exception as e:
        print(f"Error parsing expense: {e}")
        return {
            "success": False,
            "message": "Sorry, I had trouble processing that. Please try again.",
        }


def generate_expense_summary(expenses: list, period: str) -> str:
    """Generate a friendly summary of expenses using Gemini"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        expense_list = "\n".join(
            [
                f"{e['date']}: ${e['amount']} - {e['category']} ({e['description']})"
                for e in expenses
            ]
        )

        prompt = f"""Create a brief, friendly summary of these {period} expenses:

{expense_list}

Provide:
1. Total amount spent
2. Top 3 categories by spending
3. One brief insight or observation

Keep it concise and conversational."""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Error generating summary: {e}")
        return None
