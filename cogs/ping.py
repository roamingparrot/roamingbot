import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from license_manager import manager

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="ping", description="Check bot latency.")
    async def ping(self, interaction: Interaction):
        if not manager.has_access(interaction.user.id):
            await interaction.response.send_message("You do not have an active license.", ephemeral=True)
            return
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency: {latency}ms")

def setup(bot):
    bot.add_cog(Ping(bot))
