import os
import discord
from dotenv import load_dotenv

#from discord.ext import commands
import interactions

import requests as re
from requests.auth import HTTPBasicAuth
import json

from datetime import datetime
import time

# getting relevant data from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# setting intents for Discord
intents = discord.Intents.default()
intents.members = True

bot = interactions.Client(token=TOKEN)

# We'll be issuing requests to our Planning Center account

# authorisation data
username = "980b4f11ce7d52fc9a5a20fc8a89d5d0c4dd1dd733d7b9e36ebbc6a9e1b98992"
password = "c68fdcd2c0d8811501f6b9a64c0e0b86a44836b5a23f2f4d7c5a525d1dce538d"

# get plan IDs for upcoming Sundays
getUpcomingSundays = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans?filter=future', auth=HTTPBasicAuth(username, password))
d_getUpcomingSundays = json.loads(getUpcomingSundays.text)

upcomingSundayList = []
idUpcomingSundays = []
for x in d_getUpcomingSundays['data']:
    idUpcomingSundays.append(x['id'])
    upcomingSundayList.append(x['attributes']['dates'])

print("Up and running")

# defining bot commands and events
# @bot.event
# async def on_ready():
#     guild = discord.utils.get(bot.guilds, name=GUILD)

#     print(
#         f'{bot.user} has connected to Discord, to the following guild:\n'
#         f'{guild.name}(id:{guild.id})'
#     )

#     members = '\n - '.join([member.name for member in guild.members])
#     print(f'Guild Members: \n - {members}')

# @bot.event
# async def on_member_join(member):
#     await member.create_dm()
#     await member.dm_channel.send(
#         f"H i {member.name}, welcome to my Discord server!"
#     )

# @bot.command(name="test", description="blah blah", scope="863761135793340416")
# async def test(ctx, arg):
#     await ctx.channel.send(arg)

@bot.command(name="upcoming-sundays",  description="blah blah", scope="863761135793340416")
async def upcoming_sundays(ctx: interactions.CommandContext):
    dates = []
    for i in d_getUpcomingSundays["data"]:
        dates.append(i["attributes"]["dates"])

    response = "Here are the upcoming Sundays that have complete plans: "

    for date in dates:
        response += f"\n{date}"
    
    await ctx.send(response)

@bot.command(name="next-sunday-info",  description="blah blah", scope="863761135793340416") # not implemented ye,  description="blah blah"t
async def next_sunday_info(ctx: interactions.CommandContext):
    getNextSunday = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idUpcomingSundays[0], auth=HTTPBasicAuth(username, password))
    d_getNextSunday = json.loads(getNextSunday.text)

    # get_songs()

    pass

@bot.command(name="next-sunday-team",  description="blah blah", scope="863761135793340416")
async def next_sunday_team(ctx: interactions.CommandContext, date=upcomingSundayList[0]):

    for d in d_getUpcomingSundays['data']:
        date1 = datetime.strptime(d['attributes']['dates'], "%d %B %Y")
        if date == upcomingSundayList[0]:
            date2 = datetime.strptime(date, "%d %B %Y")
        else:
            date2 = datetime.strptime(date, "%b%d")
            

        if date1.strftime("%b%d") == date2.strftime("%b%d"):
            idSelectedSunday = d['id']

    getNextSundayTeam = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idSelectedSunday+'/team_members', auth=HTTPBasicAuth(username, password))
    d_getNextSundayTeam = json.loads(getNextSundayTeam.text)

    confirmedTeamMembers = []
    unconfirmedTeamMembers = []
    declinedTeamMembers = []


    for i in range(len(d_getNextSundayTeam['data'])):
        teamMember = {
            "index": i+1,
            "pc_id": "",
            "name": "",
            "team_position": "",
            "status": ""

        }

        teamMember['pc_id'] = d_getNextSundayTeam['data'][i]['id']
        teamMember['name'] = d_getNextSundayTeam['data'][i]['attributes']['name']
        teamMember['team_position'] = d_getNextSundayTeam['data'][i]['attributes']['team_position_name']
        teamMember['status'] = d_getNextSundayTeam['data'][i]['attributes']['status']

        if d_getNextSundayTeam['data'][i]['attributes']['status'] == 'C':        
            confirmedTeamMembers.append(teamMember)
        elif d_getNextSundayTeam['data'][i]['attributes']['status'] == 'U':
            unconfirmedTeamMembers.append(teamMember)
        elif d_getNextSundayTeam['data'][i]['attributes']['status'] == 'D':
            declinedTeamMembers.append(teamMember)

    response = ""

    # print out confirmed team members
    response += "\nConfirmed team members:"

    confirmedTeamMemberIndex = 1

    if len(confirmedTeamMembers) < 1:
        response += "\nNone."
    else:
        for i in confirmedTeamMembers:
            response += "\n{}. {} - {}".format(i['index'], i['name'], i['team_position'])
        # confirmedTeamMemberIndex+=1

    response += "\n\nUnconfirmed team members:"
    if len(unconfirmedTeamMembers) < 1:
        response += "\nNone."
    else:
        unconfirmedCount = 1
        for i in unconfirmedTeamMembers:
            response += "\n{}. {} - {}".format(i['index'], i['name'], i['team_position'])

    response += "\n\nTeam members that declined:"

    if len(declinedTeamMembers) < 1:
        response += "\nNone."
    else:
        for i in declinedTeamMembers:
            response += "\n{}. {} - {}".format(i['index'], i['name'], i['team_position'])


    response += "\n\nUse the $update-sunday-team command to confirm member availability."

    await ctx.send(response)

# include command for getting
@bot.command(name="get-songs",  description="blah blah", scope="863761135793340416")
async def get_songs(ctx: interactions.CommandContext):
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

@bot.command(name="update-sunday-team",  description="blah blah", scope="863761135793340416")
async def update_sunday_team(ctx: interactions.CommandContext, mid: int, status_code):
    
    # for d in d_getUpcomingSundays['data']:
    #     date1 = datetime.strptime(d['attributes']['dates'], "%d %B %Y")
    #     date2 = datetime.strptime(date, "%b%d")

    #     if date1.strftime("%b%d") == date2.strftime("%b%d"):
    #         idSelectedSunday = d['id']

    getSundayTeam = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+'56678239'+'/team_members', auth=HTTPBasicAuth(username, password)) # replace the id with idSelectedSunday
    d_getSundayTeam = json.loads(getSundayTeam.text)

    teamMembers = []

    for i in range(len(d_getSundayTeam['data'])):
        teamMember = {
            "index": i+1,
            "pc_id": "",
            "name": "",
            "team_position": "",
            "status": ""

        }

        teamMember['pc_id'] = d_getSundayTeam['data'][i]['id']
        teamMember['name'] = d_getSundayTeam['data'][i]['attributes']['name']
        teamMember['team_position'] = d_getSundayTeam['data'][i]['attributes']['team_position_name']
        teamMember['status'] = d_getSundayTeam['data'][i]['attributes']['status']

        teamMembers.append(teamMember)

    for member in teamMembers:
        if member['index'] == mid:
            data = {}
            data["id"] = member['pc_id']
            data["attributes"] = {"status": status_code.upper()} # should really do some error handling here; CommandNotFound. MissingRequiredArgument

            updated_member = member['name']

            update = {"data": data}

            url = "https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/{}/team_members/{}".format('56678239', member['pc_id']) # replace the id with idSelectedSunday
            print(data)
            print(url)
            r = re.patch(url, json=update, auth=HTTPBasicAuth(username, password))
            print(r.request.url)
            print(r.request.body)
            print(r.request.headers)
            print(r.status_code)
    await ctx.send(f"Status for {updated_member} updated.")

# @update_sunday_team.error
# async def update_sunday_team_error(ctx, error):
#     if isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send("Make sure you put in all the parameters for this command. Send $help command-name-here to get help on a command.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"{error}; did you type out your command correctly?")

bot.start()
