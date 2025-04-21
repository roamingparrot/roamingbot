# Modular Discord Bot with Slash Commands

## Features
- Modular design with cogs
- Slash command support (e.g., `/hello`)
- Error handling for user-friendly feedback

## Cross-Platform Compatibility
This bot works on **Windows**, **macOS**, and **Linux**. Follow the setup instructions below for your OS.

### Prerequisites
- **Python 3.8+** must be installed. Download from [python.org](https://www.python.org/downloads/).
- Recommended: Use a virtual environment (venv).

## Setup

### 1. Install dependencies
**Windows/macOS/Linux:**
```sh
pip install -r requirements.txt
```

### 2. Set your bot token in a `.env` file
Create a file named `.env` in the project folder and add:
```env
DISCORD_TOKEN=YOUR_BOT_TOKEN
```

### 3. Run the bot
**Windows:**
```bat
python bot.py
```
**macOS/Linux:**
```sh
python3 bot.py
```

## Adding More Commands
- Add new `.py` files in the `cogs` folder and define new classes inheriting from `commands.Cog`.
- Use `@nextcord.slash_command` for new slash commands.

## Example Slash Command
- `/hello` — Replies with a greeting mentioning the user.

## Security
- **Never share your bot token publicly!**
