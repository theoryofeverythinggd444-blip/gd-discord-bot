import discord
from discord import app_commands
import requests
import os

class GDClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced successfully!")

bot = GDClient()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Your Geometry Dash bot is online and ready!")

# 1. LEVEL BY ID COMMAND
@bot.tree.command(name="level", description="Get Geometry Dash level info by ID")
@app_commands.describe(level_id="The ID of the Geometry Dash level")
async def level_info(interaction: discord.Interaction, level_id: str):
    await interaction.response.defer(thinking=True)

    response = requests.get(f"https://gdbrowser.com/api/level/{level_id}")
    
    if response.status_code != 200:
        await interaction.followup.send("❌ Level not found or GD servers are down!")
        return

    data = response.json()

    diff_name = data.get("difficulty", "Unrated")
    stars = data.get("stars", 0)
    face_name = data.get("difficultyFace", "unrated")
    icon_url = f"https://gdbrowser.com/assets/difficulties/{face_name}.png"

    embed = discord.Embed(
        title=f"{data.get('name')} (ID: {data.get('id')})",
        description=f"Created by **{data.get('author')}**",
        color=discord.Color.gold() if data.get("featured") else discord.Color.green()
    )
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name="Difficulty", value=diff_name, inline=True)
    embed.add_field(name="Stars", value=f"⭐ {stars}", inline=True)
    embed.add_field(name="Coins", value=f"🪙 {data.get('coins', 0)}", inline=True)
    embed.add_field(name="Downloads", value=f"📥 {data.get('downloads', 0):,}", inline=True)
    embed.add_field(name="Likes", value=f"👍 {data.get('likes', 0):,}", inline=True)
    embed.add_field(name="Objects", value=f"🧩 {data.get('objects', 0):,}", inline=True)
    embed.add_field(name="Song", value=f"🎵 {data.get('songName')} by {data.get('songAuthor')}", inline=False)

    footer_text = []
    if data.get("epic"):
        footer_text.append("🔥 Epic Level")
    elif data.get("featured"):
        footer_text.append("⭐ Featured Level")
    
    if footer_text:
        embed.set_footer(text=" | ".join(footer_text))

    await interaction.followup.send(embed=embed)


# 2. SEARCH LEVELS BY NAME COMMAND
@bot.tree.command(name="search", description="Search for Geometry Dash levels by name")
@app_commands.describe(query="The name of the level to search for")
async def search_levels(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)

    response = requests.get(f"https://gdbrowser.com/api/search/{query}")
    
    if response.status_code != 200 or not response.json():
        await interaction.followup.send(f"❌ No levels found matching `{query}`.")
        return

    levels = response.json()[:5]

    embed = discord.Embed(
        title=f"🔍 Search Results for '{query}'",
        color=discord.Color.blue()
    )

    for lvl in levels:
        embed.add_field(
            name=f"{lvl.get('name')} (ID: {lvl.get('id')})",
            value=f"By: **{lvl.get('author')}** | ⭐ {lvl.get('stars', 0)} | 📥 {lvl.get('downloads', 0):,}",
            inline=False
        )

    await interaction.followup.send(embed=embed)


# 3. PLAYER PROFILE COMMAND WITH PLAYER ICON
@bot.tree.command(name="player", description="Get Geometry Dash player stats by username")
@app_commands.describe(username="The username of the player")
async def player_profile(interaction: discord.Interaction, username: str):
    await interaction.response.defer(thinking=True)

    response = requests.get(f"https://gdbrowser.com/api/profile/{username}")
    
    if response.status_code != 200:
        await interaction.followup.send(f"❌ Player `{username}` not found!")
        return

    data = response.json()
    player_name = data.get('username')

    icon_url = f"https://gdbrowser.com/icon/{player_name}"

    embed = discord.Embed(
        title=f"👤 Player Profile: {player_name}",
        color=discord.Color.purple()
    )
    
    embed.set_thumbnail(url=icon_url)

    embed.add_field(name="Stars", value=f"⭐ {data.get('stars', 0):,}", inline=True)
    embed.add_field(name="Demons", value=f"😈 {data.get('demons', 0):,}", inline=True)
    embed.add_field(name="Creator Points", value=f"🛠️ {data.get('creatorPoints', 0)}", inline=True)
    embed.add_field(name="Coins", value=f"🪙 {data.get('coins', 0):,}", inline=True)
    embed.add_field(name="User Coins", value=f"🥈 {data.get('userCoins', 0):,}", inline=True)
    embed.add_field(name="Diamonds", value=f"💎 {data.get('diamonds', 0):,}", inline=True)

    if data.get('globalRank'):
        embed.set_footer(text=f"Global Rank: #{data.get('globalRank'):,}")

    await interaction.followup.send(embed=embed)

# Secure token retrieval from environment variables
bot.run(os.environ.get("DISCORD_TOKEN"))
  
