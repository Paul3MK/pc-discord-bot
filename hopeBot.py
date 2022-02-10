import os
import discord
from dotenv import load_dotenv

from discord.ext import commands

import requests as re
from requests.auth import HTTPBasicAuth
import json

# getting relevant data from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# setting intents for Discord
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

# We'll be issuing requests to our Planning Center account

# authorisation data
username = "980b4f11ce7d52fc9a5a20fc8a89d5d0c4dd1dd733d7b9e36ebbc6a9e1b98992"
password = "c68fdcd2c0d8811501f6b9a64c0e0b86a44836b5a23f2f4d7c5a525d1dce538d"

# get plan IDs for upcoming Sundays
getUpcomingSundays = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans?filter=future', auth=HTTPBasicAuth(username, password))
d_getUpcomingSundays = json.loads(getUpcomingSundays.text)
idUpcomingSundays = []
for x in d_getUpcomingSundays['data']:
    idUpcomingSundays.append(x['id'])

print("Up and running")

# defining bot commands and events
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)

    print(
        f'{bot.user} has connected to Discord, to the following guild:\n'
        f'{guild.name}(id:{guild.id})'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members: \n - {members}')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f"H i {member.name}, welcome to my Discord server!"
    )

@bot.command()
async def test(ctx, arg):
    await ctx.channel.send(arg)

# include command for getting
@bot.command(name="get_songs")
async def get_songs(ctx):
    # make request for next Sunday
    getNextSunday = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idUpcomingSundays[0], auth=HTTPBasicAuth(username, password))
    d_getNextSunday = json.loads(getNextSunday.text)

    # get songs for given Sunday
    sundaySongs = []
    getSundaySongs = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idUpcomingSundays[0]+'/items', auth=HTTPBasicAuth(username, password))
    d_getSundaySongs = json.loads(getSundaySongs.text)

    for i in range(len(d_getSundaySongs['data'])):
        if d_getSundaySongs['data'][i]['attributes']['item_type'] == 'song':
            sundaySongs.append(i)
    
    # respond to song query for a given Sunday
    songQueryResponse = "{} songs will be played on Sunday {}.".format(
        len(sundaySongs),
        d_getNextSunday['data']['attributes']['dates'])
    for s in range(len(sundaySongs)):
        songQueryResponse + "\n{}. {} in the key of {}".format(
            s,
            d_getSundaySongs['data'][sundaySongs[s]]['attributes']['title'],
            d_getSundaySongs['data'][sundaySongs[s]]['attributes']['key_name'],
        )

    await ctx.send(songQueryResponse)


bot.run(TOKEN)
