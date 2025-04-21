import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import os

TOKEN = os.getenv('DISCORD_TOKEN')

intents = nextcord.Intents.default()
intents.message_content = True  # Enable message content intent for prefix commands
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    await bot.sync_all_application_commands()
    print("Slash commands synced!")

@bot.event
async def on_application_command_error(interaction, error):
    if hasattr(error, 'original'):
        error = error.original
    await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

# Load cogs from the cogs folder
def load_cogs(bot, cogs):
    for cog in cogs:
        bot.load_extension(cog)

initial_extensions = [
    'cogs.license',
    'cogs.profitable_commands',
    'cogs.verify',
]

if __name__ == "__main__":
    load_cogs(bot, initial_extensions)
    bot.run(TOKEN)
