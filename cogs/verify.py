import nextcord
from nextcord.ext import commands
from nextcord import Interaction, ButtonStyle
from nextcord.ui import Button, View
import traceback

VERIFIED_ROLE_ID = 1265351042464354429  # Set this to your Verified role's ID
OWNER_ID = 1212843947152515142   # Replace with your Discord user ID if different

class VerifyView(View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @nextcord.ui.button(label="Verify", style=ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, button: Button, interaction: Interaction):
        # Note: This button is not restricted by user ID, anyone can verify themselves
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message(f"Verification role with ID {self.role_id} not found. Please contact an admin.", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message("You are already verified!", ephemeral=True)
            return
        try:
            await member.add_roles(role, reason="User verified via button")
            await interaction.response.send_message(f"You have been verified and given the role: {role.name}", ephemeral=True)
        except nextcord.Forbidden:
            await interaction.response.send_message(
                "I do not have permission to assign the verification role. Please check my permissions and role position.", ephemeral=True)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[ERROR] Exception in verify_button: {e}\n{tb}")
            await interaction.response.send_message(
                f"An unexpected error occurred. Please contact an admin.", ephemeral=True)

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        description="Owner only: Post a persistent verification button for users to get the Verified role.",
        default_member_permissions=nextcord.Permissions.none(),
        dm_permission=False
    )
    async def verify(self, interaction: Interaction):
        # Note: Only the owner can use this command to post the verification button, but anyone can verify themselves using the button
        if interaction.user.id != OWNER_ID:
            await interaction.send("Only the owner can use this command.", ephemeral=True)
            return
        guild = interaction.guild
        role = guild.get_role(VERIFIED_ROLE_ID)
        if not role:
            await interaction.send(f"Verification role with ID {VERIFIED_ROLE_ID} not found. Please contact an admin.", ephemeral=True)
            return
        embed = nextcord.Embed(title="Verification", description="Click the button below to verify yourself and get access to the server!", color=0x00ff00)
        view = VerifyView(role.id)
        await interaction.send(embed=embed, view=view, ephemeral=False)  # Persistent message

def setup(bot):
    bot.add_cog(Verify(bot))
