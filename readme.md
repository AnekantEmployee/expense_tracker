# Expense Tracker Telegram Bot

A smart expense tracking bot powered by Gemini AI that helps you log and analyze your spending through natural language.

## Features

- 💬 Natural language expense logging ("coffee 5", "lunch 23.50 with friends")
- 📊 Daily, weekly, and monthly summaries
- 🏷️ Automatic categorization
- 💾 Local SQLite database
- 🤖 Powered by Google Gemini AI

## Setup

1. **Install dependencies:**
```bash
   npm install
```

2. **Get your API keys:**
   - Telegram Bot Token: Talk to [@BotFather](https://t.me/botfather) on Telegram
   - Gemini API Key: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **Configure environment:**
   Create a `.env` file:
```env
   TELEGRAM_BOT_TOKEN=your_telegram_token
   GEMINI_API_KEY=your_gemini_api_key
```

4. **Run the bot:**
```bash
   npm start
```

   For development with auto-reload:
```bash
   npm run dev
```

## Usage

Send natural language messages to your bot:
- `coffee 5` - Log $5 for coffee
- `lunch 23.50 italian place` - Log lunch with description
- `uber to airport 45` - Log transport expense

Commands:
- `/today` - View today's expenses
- `/week` - View this week's expenses
- `/month` - View this month's expenses
- `/help` - Show help message

## Deployment

Deploy to Railway, Render, or Fly.io. Make sure to:
1. Set environment variables
2. The bot needs to run 24/7 (not serverless)
3. SQLite database will persist on disk

## Tech Stack

- Node.js
- Telegram Bot API
- Google Gemini AI
- SQLite (better-sqlite3)