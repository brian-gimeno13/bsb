import json
import os

from fuzzywuzzy import fuzz, process

import discord
from discord import app_commands
from dotenv import load_dotenv

from views.button import Difficulty

load_dotenv()
GUILD_ID = os.getenv('GUILD_ID')
TOKEN = os.getenv('TOKEN')
MOD_CHAT = int(os.getenv('MOD_CHAT'))
MY_GUILD = discord.Object(GUILD_ID)

song_data = {}
event_data = {}

date_format = "%a, %b %d, %Y @ %I:%M %p"


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


with open('songs.json', encoding='utf-8') as json_data:
    song_data = json.load(json_data)

intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
@app_commands.rename(song='name')
@app_commands.describe(song='Name of the requested song')
async def video(interaction: discord.Interaction, song: str):
    """Posts the requested song in both Normal and Easy mode, if possible"""
    result = process.extractOne(song, song_data.keys(), scorer=fuzz.token_sort_ratio)
    best_match = song_data[result[0]]
    view = Difficulty(best_match, interaction.user)
    await interaction.response.send_message(best_match['Normal'], view=view)


@client.tree.context_menu(name='Report User')
@app_commands.describe(reason='Reason for Report')
async def report_user(interaction: discord.Interaction, member: discord.Member):
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(
        f'Thanks for reporting {member} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(MOD_CHAT)  # replace with your channel id

    embed = discord.Embed(title='User Report')
    embed.description = member.mention

    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.add_field(name='Join Date', value=member.joined_at.strftime(date_format), inline=False)
    embed.timestamp = interaction.created_at
    embed.set_footer(text=f'Reported by {interaction.user.display_name}')

    await log_channel.send(embed=embed)


@client.tree.context_menu(name='Report Message')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # We're sending this response message with ephemeral=True, so only the command executor can see it
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(MOD_CHAT)  # replace with your channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.add_field(name="Reporter", value=interaction.user, inline=False)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)


client.run(TOKEN)
