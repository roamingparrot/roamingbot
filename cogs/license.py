import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from license_manager import manager
import os

OWNER_ID = int(os.getenv("OWNER_ID", "0"))
ADMIN_ROLE_IDS = [int(r.strip()) for r in os.getenv("LICENSE_ADMIN_ROLES", "").split(",") if r.strip().isdigit()]
OWNER_ALERT_CHANNEL_ID = int(os.getenv("OWNER_ALERT_CHANNEL_ID", "0"))

LICENSE_ACTIONS = [
    ("Add Time", "Add days to a user's license"),
    ("Remove Time", "Remove days from a user's license"),
    ("Lifetime", "Grant lifetime access to a user"),
    ("Revoke", "Revoke a user's license"),
    ("Check", "Check a user's license status"),
    ("Remove Staff", "Remove admin roles from a user"),
]

def is_owner(interaction):
    return interaction.user.id == OWNER_ID

def is_admin():
    async def predicate(interaction: Interaction):
        if is_owner(interaction):
            return True
        for role in interaction.user.roles:
            if role.id in ADMIN_ROLE_IDS:
                return True
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return False
    return commands.check(predicate)

class UserAndDaysModal(nextcord.ui.Modal):
    def __init__(self, title, action):
        super().__init__(title=title)
        self.action = action
        self.add_item(nextcord.ui.TextInput(label="User (username#discrim or ID)", placeholder="Enter the user's Discord tag or ID", required=True))
        self.add_item(nextcord.ui.TextInput(label="Days", placeholder="Enter number of days", required=True))

    async def callback(self, interaction: Interaction):
        user_input = self.children[0].value.strip()
        days = int(self.children[1].value.strip())
        user_id = None
        # Try to resolve as ID
        if user_input.isdigit():
            user_id = int(user_input)
        else:
            # Try to resolve as username#discrim
            if "#" in user_input:
                name, discrim = user_input.rsplit("#", 1)
                member = nextcord.utils.get(interaction.guild.members, name=name, discriminator=discrim)
                if member:
                    user_id = member.id
        if not user_id:
            await interaction.response.send_message("User not found. Please enter a valid Discord ID or username#discrim.", ephemeral=True)
            return
        if self.action == "Add Time":
            if user_id == OWNER_ID and not is_owner(interaction):
                await interaction.response.send_message("You cannot modify the owner's license.", ephemeral=True)
                return
            result = manager.add_time(user_id, days)
            await interaction.response.send_message(result, ephemeral=True)
        elif self.action == "Remove Time":
            if user_id == OWNER_ID and not is_owner(interaction):
                await interaction.response.send_message("You cannot modify the owner's license.", ephemeral=True)
                return
            result = manager.remove_time(user_id, days)
            await interaction.response.send_message(result, ephemeral=True)

class UserOnlyModal(nextcord.ui.Modal):
    def __init__(self, title, action):
        super().__init__(title=title)
        self.action = action
        self.add_item(nextcord.ui.TextInput(label="User ID", placeholder="Enter the user's Discord ID", required=True))

    async def callback(self, interaction: Interaction):
        user_id = int(self.children[0].value.strip())
        if self.action == "Lifetime":
            if user_id == OWNER_ID and not is_owner(interaction):
                await interaction.response.send_message("You cannot modify the owner's license.", ephemeral=True)
                return
            result = manager.grant_lifetime(user_id)
            await interaction.response.send_message(result, ephemeral=True)
        elif self.action == "Revoke":
            if user_id == OWNER_ID and not is_owner(interaction):
                await interaction.response.send_message("You cannot revoke the owner's license.", ephemeral=True)
                return
            result = manager.revoke(user_id)
            await interaction.response.send_message(result, ephemeral=True)
        elif self.action == "Check":
            result = manager.get_expiry(user_id)
            await interaction.response.send_message(result, ephemeral=True)
        elif self.action == "Remove Staff":
            if not is_owner(interaction):
                await interaction.response.send_message("Only the owner can use this command.", ephemeral=True)
                return
            guild = interaction.guild
            member = guild.get_member(user_id)
            if member is None:
                await interaction.response.send_message("User not found in this server.", ephemeral=True)
                return
            removed_roles = []
            for role in member.roles:
                if role.id in ADMIN_ROLE_IDS:
                    try:
                        await member.remove_roles(role, reason="Removed from staff by owner command")
                        removed_roles.append(role.name)
                    except Exception as e:
                        await interaction.response.send_message(f"Failed to remove role {role.name}: {e}", ephemeral=True)
                        return
            if removed_roles:
                await interaction.response.send_message(f"Removed staff roles from <@{user_id}>: {', '.join(removed_roles)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"User <@{user_id}> had no staff roles to remove.", ephemeral=True)

class LicenseActionSelect(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label=label, description=desc)
            for label, desc in LICENSE_ACTIONS
        ]
        super().__init__(
            placeholder="Choose a license action...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):
        action = self.values[0]
        if action in ["Add Time", "Remove Time"]:
            await interaction.response.send_modal(UserAndDaysModal(title=action, action=action))
        else:
            await interaction.response.send_modal(UserOnlyModal(title=action, action=action))

class LicenseActionView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(LicenseActionSelect())

class License(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="license", description="Manage user licenses.", guild_ids=[1265341386471899217])
    @is_admin()
    async def license(self, interaction: Interaction):
        embed = nextcord.Embed(
            title="License Management Panel",
            description="Select a license action to perform.",
            color=nextcord.Color.dark_gold()
        )
        await interaction.response.send_message(embed=embed, view=LicenseActionView(), ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        # Sync both global and guild commands
        try:
            await self.bot.sync_all_application_commands()
            print("Synced all global commands!")
            await self.bot.sync_all_application_commands(guild_ids=[1265341386471899217])
            print("Synced all guild commands!")
        except Exception as e:
            print(f"Command sync error: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        before_roles = set(r.id for r in before.roles)
        after_roles = set(r.id for r in after.roles)
        alert_roles = set(ADMIN_ROLE_IDS)
        # Promotions
        new_admin_roles = after_roles - before_roles
        promoted = new_admin_roles & alert_roles
        # Removals
        removed_admin_roles = before_roles - after_roles
        demoted = removed_admin_roles & alert_roles
        if promoted and OWNER_ALERT_CHANNEL_ID:
            channel = after.guild.get_channel(OWNER_ALERT_CHANNEL_ID)
            if channel:
                role_names = [after.guild.get_role(rid).name for rid in promoted]
                await channel.send(f"⚠️ <@{OWNER_ID}> ALERT: {after.mention} was promoted to admin role(s): {', '.join(role_names)}")
        if demoted and OWNER_ALERT_CHANNEL_ID:
            channel = after.guild.get_channel(OWNER_ALERT_CHANNEL_ID)
            if channel:
                role_names = [after.guild.get_role(rid).name for rid in demoted]
                await channel.send(f"⚠️ <@{OWNER_ID}> ALERT: {after.mention} was removed from admin role(s): {', '.join(role_names)}")

def setup(bot):
    bot.add_cog(License(bot))
