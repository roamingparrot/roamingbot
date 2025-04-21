import nextcord
from nextcord.ext import commands
from nextcord import Interaction, ButtonStyle, SlashOption
from nextcord.ui import Button, View

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

    @nextcord.slash_command(description="Show a verification button for users to get a role.")
    async def verify(self, interaction: Interaction, role: nextcord.Role = SlashOption(description="Role to assign when verified")):
        embed = nextcord.Embed(title="Verification", description="Click the button below to verify yourself and get access to the server!", color=0x00ff00)
        view = VerifyView(role.id)
        await interaction.send(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(Verify(bot))
