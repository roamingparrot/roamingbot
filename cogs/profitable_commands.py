import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from license_manager import manager
import json
import os

REQUEST_CHANNEL_ID = os.getenv("REQUEST_CHANNEL_ID")
if REQUEST_CHANNEL_ID:
    try:
        REQUEST_CHANNEL_ID = int(REQUEST_CHANNEL_ID)
    except ValueError:
        REQUEST_CHANNEL_ID = None

ITEMS_FILE = os.path.join(os.path.dirname(__file__), '..', 'items.json')

CATEGORIES = [
    ("Sneakers", None),
    ("Watches", None),
    ("Streetwear", None),
    ("Accessories", None),
]

class Profitable(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="profitable", description="Find the most profitable items to resell.", guild_ids=[1265341386471899217])
    async def profitable(self, interaction: Interaction):
        if not manager.has_access(interaction.user.id):
            await interaction.response.send_message("You need an active license to use this command.", ephemeral=True)
            return
        embed = nextcord.Embed(
            title=f"{interaction.user.display_name}'s Resell Panel",
            description=(
                "These are the most profitable items to resell right now.\n"
                "Choose a category from the dropdown menu below:"
            ),
            color=nextcord.Color.purple()
        )
        await interaction.response.send_message(embed=embed, view=CategoryView(), ephemeral=True)

    @nextcord.slash_command(name="additem", description="Add a new item to a category (owner only)", guild_ids=[1265341386471899217])
    async def additem(self, interaction: Interaction):
        OWNER_ID = int(os.getenv("OWNER_ID", "0"))
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("Only the owner can add items.", ephemeral=True)
            return
        embed = nextcord.Embed(
            title="Add Item",
            description="Select a category to add a new item.",
            color=nextcord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=AddItemCategoryView(OWNER_ID), ephemeral=True)

    @nextcord.slash_command(name="edititem", description="Edit an existing item (owner only)", guild_ids=[1265341386471899217])
    async def edititem(self, interaction: Interaction):
        OWNER_ID = int(os.getenv("OWNER_ID", "0"))
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("Only the owner can edit items.", ephemeral=True)
            return
        items_data = load_items()
        categories = list(items_data.keys())
        options = [nextcord.SelectOption(label=cat) for cat in categories]
        select = nextcord.ui.Select(placeholder="Select a category...", options=options)
        view = nextcord.ui.View(timeout=60)
        view.add_item(select)
        async def select_callback(interaction2: Interaction):
            cat = select.values[0]
            items = items_data[cat]["items"]
            if not items:
                await interaction2.response.send_message("No items to edit in this category.", ephemeral=True)
                return
            item_options = [nextcord.SelectOption(label=item["name"]) for item in items]
            item_select = nextcord.ui.Select(placeholder="Select item to edit...", options=item_options)
            item_view = nextcord.ui.View(timeout=60)
            item_view.add_item(item_select)
            async def item_select_callback(interaction3: Interaction):
                item_name = item_select.values[0]
                class EditItemModal(nextcord.ui.Modal):
                    def __init__(self):
                        super().__init__(title=f"Edit {item_name}")
                        self.add_item(nextcord.ui.TextInput(label="Name", default=item_name, required=True))
                        self.add_item(nextcord.ui.TextInput(label="Link", default=next((i["link"] for i in items if i["name"] == item_name), ""), required=False))
                        self.add_item(nextcord.ui.TextInput(label="Purchase Price", default=str(next((i["purchase_price"] for i in items if i["name"] == item_name), "")), required=True))
                    async def callback(self, interaction4: Interaction):
                        for i in items:
                            if i["name"] == item_name:
                                i["name"] = self.children[0].value
                                i["link"] = self.children[1].value
                                i["purchase_price"] = float(self.children[2].value)
                        save_items(items_data)
                        await interaction4.response.send_message(f"Item '{item_name}' updated.", ephemeral=True)
                await interaction3.response.send_modal(EditItemModal())
            item_select.callback = item_select_callback
            await interaction2.response.send_message(f"Select an item to edit from {cat}:", view=item_view, ephemeral=True)
        select.callback = select_callback
        await interaction.response.send_message("Select a category to edit an item from:", view=view, ephemeral=True)

    @nextcord.slash_command(name="removeitem", description="Remove an item from a category (owner only)", guild_ids=[1265341386471899217])
    async def removeitem(self, interaction: Interaction):
        OWNER_ID = int(os.getenv("OWNER_ID", "0"))
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("Only the owner can remove items.", ephemeral=True)
            return
        items_data = load_items()
        categories = list(items_data.keys())
        options = [nextcord.SelectOption(label=cat) for cat in categories]
        select = nextcord.ui.Select(placeholder="Select a category...", options=options)
        view = nextcord.ui.View(timeout=60)
        view.add_item(select)
        async def select_callback(interaction2: Interaction):
            cat = select.values[0]
            items = items_data[cat]["items"]
            if not items:
                await interaction2.response.send_message("No items to remove in this category.", ephemeral=True)
                return
            item_options = [nextcord.SelectOption(label=item["name"]) for item in items]
            item_select = nextcord.ui.Select(placeholder="Select item to remove...", options=item_options)
            item_view = nextcord.ui.View(timeout=60)
            item_view.add_item(item_select)
            async def item_select_callback(interaction3: Interaction):
                item_name = item_select.values[0]
                items_data[cat]["items"] = [i for i in items if i["name"] != item_name]
                save_items(items_data)
                await interaction3.response.send_message(f"Removed item '{item_name}' from {cat}.", ephemeral=True)
            item_select.callback = item_select_callback
            await interaction2.response.send_message(f"Select an item to remove from {cat}:", view=item_view, ephemeral=True)
        select.callback = select_callback
        await interaction.response.send_message("Select a category to remove an item from:", view=view, ephemeral=True)

def load_items():
    with open(ITEMS_FILE, 'r') as f:
        return json.load(f)

def save_items(data):
    with open(ITEMS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

class CategoryView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CategorySelect())

class CategorySelect(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label=cat) if desc is None else nextcord.SelectOption(label=cat, description=desc)
            for cat, desc in CATEGORIES
        ]
        super().__init__(
            placeholder="Choose a category to resell...",
            min_values=1,
            max_values=1,
            options=options
        )
    async def callback(self, interaction: Interaction):
        category = self.values[0]
        await interaction.response.send_message(f"You selected: {category}.", ephemeral=True)

class AddItemCategoryView(nextcord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=60)
        self.add_item(AddItemCategorySelect(owner_id))

class AddItemCategorySelect(nextcord.ui.Select):
    def __init__(self, owner_id):
        options = [nextcord.SelectOption(label=cat) for cat, _ in CATEGORIES]
        super().__init__(
            placeholder="Select a category to add an item...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.owner_id = owner_id
    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(f"Add item to: {self.values[0]}", ephemeral=True)

def setup(bot):
    bot.add_cog(Profitable(bot))
