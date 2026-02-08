import os
import logging
from datetime import date
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

from llm_parser import parse_expense_message, generate_expense_summary
from database import (
    save_expense,
    get_today_expenses,
    get_week_expenses,
    get_month_expenses,
    get_category_summary,
)

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Category emoji mapping
CATEGORY_EMOJI = {
    "food": "🍔",
    "coffee": "☕",
    "transport": "🚗",
    "groceries": "🛒",
    "entertainment": "🎬",
    "shopping": "🛍️",
    "bills": "📄",
    "health": "💊",
    "other": "💰",
    "uncategorized": "❓",
}


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:.2f}"


def get_category_emoji(category: str) -> str:
    """Get emoji for category"""
    return CATEGORY_EMOJI.get(category.lower(), "💰")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """👋 Welcome to Expense Tracker!

Just send me your expenses in natural language:
- "coffee 5"
- "lunch 23.50 with Sarah"
- "uber 15"
- "groceries 67.80"

Commands:
/today - Today's expenses
/week - This week's expenses  
/month - This month's expenses
/help - Show this message

Let's start tracking! 💰"""

    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """📊 How to use Expense Tracker:

*Logging expenses:*
Just type naturally:
- "coffee 4.50"
- "dinner 45 italian restaurant"
- "gas 60"

*View expenses:*
/today - See today's spending
/week - See this week's spending
/month - See this month's spending

That's it! I'll handle the rest. 🎯"""

    await update.message.reply_text(help_message, parse_mode="Markdown")


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /today command"""
    user_id = update.effective_user.id

    try:
        expenses = get_today_expenses(user_id)

        if not expenses:
            await update.message.reply_text(
                "No expenses logged today. Start tracking! 💸"
            )
            return

        summary, total = get_category_summary(expenses)

        message = "📅 *Today's Expenses*\n\n"

        for category, amount in summary.items():
            emoji = get_category_emoji(category)
            message += f"{emoji} {category}: {format_currency(amount)}\n"

        message += f"\n💰 *Total: {format_currency(total)}*"

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in today_command: {e}")
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again."
        )


async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /week command"""
    user_id = update.effective_user.id

    try:
        expenses = get_week_expenses(user_id)

        if not expenses:
            await update.message.reply_text("No expenses logged this week.")
            return

        summary, total = get_category_summary(expenses)

        message = "📊 *This Week's Expenses*\n\n"

        for category, amount in summary.items():
            emoji = get_category_emoji(category)
            message += f"{emoji} {category}: {format_currency(amount)}\n"

        message += f"\n💰 *Total: {format_currency(total)}*"
        message += f"\n📝 {len(expenses)} transactions"

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in week_command: {e}")
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again."
        )


async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /month command"""
    user_id = update.effective_user.id

    try:
        expenses = get_month_expenses(user_id)

        if not expenses:
            await update.message.reply_text("No expenses logged this month.")
            return

        summary, total = get_category_summary(expenses)

        # Sort categories by amount
        sorted_categories = sorted(summary.items(), key=lambda x: x[1], reverse=True)

        message = "📈 *This Month's Expenses*\n\n"

        for category, amount in sorted_categories:
            emoji = get_category_emoji(category)
            percentage = (amount / total) * 100
            message += (
                f"{emoji} {category}: {format_currency(amount)} ({percentage:.1f}%)\n"
            )

        message += f"\n💰 *Total: {format_currency(total)}*"
        message += f"\n📝 {len(expenses)} transactions"

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in month_command: {e}")
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages (expense logging)"""
    user_id = update.effective_user.id
    user_message = update.message.text

    try:
        # Show typing indicator
        await update.message.chat.send_action("typing")

        # Parse the expense using Gemini
        parse_result = parse_expense_message(user_message)

        if not parse_result["success"]:
            await update.message.reply_text(parse_result["message"])
            return

        data = parse_result["data"]
        amount = data.get("amount")
        category = data.get("category", "other")
        description = data.get("description", "")
        needs_clarification = data.get("needs_clarification", False)
        clarification_question = data.get("clarification_question")

        # If clarification needed
        if needs_clarification:
            question = clarification_question or "Could you provide more details?"
            await update.message.reply_text(question)
            return

        # Save to database
        current_date = date.today().isoformat()
        save_expense(user_id, amount, category, description, current_date)

        # Send confirmation
        emoji = get_category_emoji(category)
        confirm_message = f"✅ Logged {format_currency(amount)}\n{emoji} {category}: {description or category or 'expense'}"

        await update.message.reply_text(confirm_message)

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't process that. Try something like 'coffee 5' or 'lunch 23.50'"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    # Get token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    # Create application
    application = Application.builder().token(token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("week", week_command))
    application.add_handler(CommandHandler("month", month_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Register error handler
    application.add_error_handler(error_handler)

    # Start bot
    logger.info("🤖 Expense tracker bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
