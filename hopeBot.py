import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} has connected to Discord, to the following guild:\n'
        f'{guild.name}(id:{guild.id})'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members: \n - {members}')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f"Hi {member.name}, welcome to my Discord server!"
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!hello':
        response = "I've already said hello"
        await message.channel.send(response)

    elif message.content == "raise-exception":
        raise discord.DiscordException



client.run(TOKEN)