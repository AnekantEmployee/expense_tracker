import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Dict, Any
from datetime import datetime, timedelta

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
                    "when": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="When the expense occurred: 'today', 'yesterday', or specific date. Default is 'today'",
                    ),
                },
                required=["amount"],
            ),
        )
    ]
)

# Define query tool for general questions
query_tool = genai.protos.Tool(
    function_declarations=[
        genai.protos.FunctionDeclaration(
            name="query_expenses",
            description="User is asking a question about their past expenses",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "query_type": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Type of query: 'check_if_logged', 'how_much_spent', 'when_did_i', 'list_expenses'",
                    ),
                    "item": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="The item/category/description user is asking about (e.g., 'panipuri', 'coffee', 'food')",
                    ),
                    "timeframe": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Time period: 'today', 'yesterday', 'this_week', 'this_month', 'all_time'",
                    ),
                },
                required=["query_type"],
            ),
        )
    ]
)


def parse_expense_message(user_message: str) -> Dict[str, Any]:
    """Parse expense message using Gemini AI"""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-3-flash-preview", tools=[expense_tool, query_tool]
        )

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        system_prompt = f"""You are an expense tracking assistant. Your job is to either:
1. Extract expense information from user messages to log them
2. Identify when user is asking a QUESTION about their past expenses

Current date: {today}
Yesterday's date: {yesterday}

IMPORTANT - Detect QUERIES vs LOGGING:
- "Did I eat panipuri this week?" → This is a QUERY (use query_expenses tool)
- "I ate panipuri 20 rs" → This is LOGGING (use log_expense tool)
- "How much did I spend on food?" → This is a QUERY
- "coffee 50" → This is LOGGING

Rules for LOGGING expenses (log_expense tool):
1. Extract the amount, category, and description from natural language
2. Common categories: food, transport, coffee, groceries, entertainment, shopping, bills, health, other
3. Currency: User is in India, so treat numbers as Indian Rupees (₹/rs/rupees). Don't add $ symbol.
4. Time detection: 
   - "yesterday morning spending of 20 rs" → when: "yesterday"
   - "I spent 50 on coffee today" → when: "today"
   - "last week I bought groceries 500" → when: specific date if possible, otherwise "yesterday" or "today"
   - Default is "today" if no time mentioned
5. If the message doesn't contain an expense or amount, set needs_clarification to true
6. Be smart about context - "coffee 5" means ₹5 for coffee, "panipuri 20" means ₹20 for panipuri
7. For ambiguous messages, ask for clarification

Rules for QUERIES (query_expenses tool):
1. Use this when user asks questions like:
   - "Did I eat panipuri this week?"
   - "How much did I spend on food?"
   - "When did I buy coffee?"
   - "Show me my breakfast expenses"
2. Identify the query_type, item, and timeframe

Examples for LOGGING:
- "coffee 5" → amount: 5, category: "coffee", description: "coffee", when: "today"
- "yesterday morning spending of 20 rs for breakfast" → amount: 20, category: "food", description: "breakfast yesterday morning", when: "yesterday"
- "lunch 23.50 with Sarah" → amount: 23.50, category: "food", description: "lunch with Sarah", when: "today"
- "uber to airport 45" → amount: 45, category: "transport", description: "uber to airport", when: "today"
- "groceries" → needs_clarification: true, clarification_question: "How much did you spend on groceries?"

Examples for QUERIES:
- "Did I ate panipuri this week?" → query_type: "check_if_logged", item: "panipuri", timeframe: "this_week"
- "How much did I spend on food today?" → query_type: "how_much_spent", item: "food", timeframe: "today"
"""

        full_prompt = f"{system_prompt}\n\nUser message: {user_message}"

        response = model.generate_content(full_prompt)

        # Check if there's a function call
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_call = part.function_call

                    # Handle query
                    if function_call.name == "query_expenses":
                        args = dict(function_call.args)
                        return {"success": True, "type": "query", "data": args}

                    # Handle expense logging
                    if function_call.name == "log_expense":
                        args = dict(function_call.args)
                        return {"success": True, "type": "expense", "data": args}

        # If no function call, return the text response
        text_response = response.text if hasattr(response, "text") else None
        return {
            "success": False,
            "message": text_response
            or "I couldn't understand that. Please try something like 'coffee 5' or 'lunch 25'",
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
                f"{e['date']}: ₹{e['amount']} - {e['category']} ({e['description']})"
                for e in expenses
            ]
        )

        prompt = f"""Create a brief, friendly summary of these {period} expenses (in Indian Rupees):

{expense_list}

Provide:
1. Total amount spent (use ₹ symbol)
2. Top 3 categories by spending
3. One brief insight or observation

Keep it concise and conversational."""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Error generating summary: {e}")
        return None
