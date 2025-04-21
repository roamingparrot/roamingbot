# Modular Discord Bot with Slash Commands

## Features
- Modular design with cogs
- Slash command support (e.g., `/hello`)
- Error handling for user-friendly feedback

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Set your bot token in a `.env` file:
   ```
   DISCORD_TOKEN=YOUR_BOT_TOKEN
   ```
3. Run the bot:
   ```
   python bot.py
   ```

## Adding More Commands
- Add new `.py` files in the `cogs` folder and define new classes inheriting from `commands.Cog`.
- Use `@nextcord.slash_command` for new slash commands.

## Example Slash Command
- `/hello` — Replies with a greeting mentioning the user.

## Security
- **Never share your bot token publicly!**
