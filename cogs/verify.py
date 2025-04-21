import nextcord
from nextcord.ext import commands
from nextcord import Interaction, ButtonStyle
from nextcord.ui import Button, View
import os

class VerifyView(View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @nextcord.ui.button(label="Verify", style=ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, button: Button, interaction: Interaction):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("Verification role not found. Please contact an admin.", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message("You are already verified!", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"You have been verified and given the role: {role.name}", ephemeral=True)

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Read the verification role ID from the environment
        try:
            self.verification_role_id = int(os.getenv("VERIFICATION_ROLE_ID", "0"))
        except ValueError:
            self.verification_role_id = 0

    @nextcord.slash_command(description="Verify yourself to get access to the server.")
    async def verify(self, interaction: Interaction):
        if not self.verification_role_id:
            await interaction.send("Verification role not set. Please contact an admin.", ephemeral=True)
            return
        embed = nextcord.Embed(title="Verification", description="Click the button below to verify yourself and get access to the server!", color=0x00ff00)
        view = VerifyView(self.verification_role_id)
        await interaction.send(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(Verify(bot))
