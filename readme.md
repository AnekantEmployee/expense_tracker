# Expense Tracker Telegram Bot 

A smart expense tracking bot powered by Google Gemini AI that helps you log and analyze your spending through natural language.

## Features

- 💬 Natural language expense logging ("coffee 5", "lunch 23.50 with friends")
- 📊 Daily, weekly, and monthly summaries
- 🏷️ Automatic categorization
- 💾 Local SQLite database
- 🤖 Powered by Google Gemini AI

## Setup

### 1. Install Python

Make sure you have Python 3.8+ installed:

```bash
python --version
```

### 2. Clone and Setup

```bash
# Create project directory
mkdir expense-bot
cd expense-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Get API Keys

**Telegram Bot Token:**

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy the token you receive

**Gemini API Key:**

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 4. Configure Environment

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_telegram_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the Bot

```bash
python main.py
```

You should see: `🤖 Expense tracker bot is running...`

## Usage

Open Telegram and find your bot. Send messages like:

**Logging expenses:**

- `coffee 5` - Log $5 for coffee
- `lunch 23.50 italian place` - Log lunch with description
- `uber to airport 45` - Log transport expense
- `groceries 67.80` - Log groceries

**View expenses:**

- `/today` - View today's expenses
- `/week` - View this week's expenses
- `/month` - View this month's expenses
- `/help` - Show help message

## Deployment

### Option 1: Railway

1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your repository
4. Add environment variables in Settings
5. Deploy

### Option 2: Render

1. Create account at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python main.py`
6. Add environment variables
7. Deploy

### Option 3: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Set secrets
fly secrets set TELEGRAM_BOT_TOKEN=your_token
fly secrets set GEMINI_API_KEY=your_key

# Deploy
fly deploy
```

## Tech Stack

- Python 3.8+
- python-telegram-bot
- Google Gemini AI
- SQLite

## Project Structure

```
expense-bot/
├── main.py           # Main bot logic
├── database.py       # Database operations
├── llm_parser.py     # Gemini AI integration
├── schema.sql        # Database schema
├── requirements.txt  # Python dependencies
├── .env             # Environment variables (create this)
└── README.md        # Documentation
```

## Troubleshooting

**Bot not responding:**

- Check if `main.py` is running
- Verify your `TELEGRAM_BOT_TOKEN` is correct
- Check internet connection

**"Error parsing expense":**

- Verify your `GEMINI_API_KEY` is correct
- Check Gemini API quota/billing

**Database errors:**

- Delete `expenses.db` and restart (will lose data)
- Check file permissions

## Future Enhancements

- Receipt image scanning
- Budget alerts
- Split expense tracking
- Multi-currency support
- Export to CSV/Excel
- Recurring expenses
- Web dashboard

## License

MIT
