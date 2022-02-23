from http import client
import os
from select import select
import discord
from dotenv import load_dotenv

from discord.ext import commands

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

bot = commands.Bot(command_prefix='.', intents=intents)

owner = bot.get_user(442801889986347018)

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

def check_null(object, entry):
    """Checks if the passed object is null, and filters it out."""
    if object is not None:
        return f"{entry}: {object}\n"
    else:
        pass

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

@bot.command(name="upcoming-sundays")
async def upcoming_sundays(ctx):
    dates = []
    for i in d_getUpcomingSundays["data"]:
        dates.append(i["attributes"]["dates"])

    response = "Here are the upcoming Sundays that have complete plans: "

    for date in dates:
        response += f"\n{date}"
    
    await ctx.send(response)

@bot.command(name="next-sunday-info") # not implemented yet
async def next_sunday_info(ctx):
    getNextSunday = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idUpcomingSundays[0], auth=HTTPBasicAuth(username, password))
    d_getNextSunday = json.loads(getNextSunday.text)

    # get_songs()

    pass

@bot.command(name="sunday-team", help="Gets the list of team members for a given Sunday. Default is next Sunday.")
async def sunday_team(ctx, date=upcomingSundayList[0]):

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
    response += "\n> Confirmed team members:"

    confirmedTeamMemberIndex = 1

    if len(confirmedTeamMembers) < 1:
        response += "\nNone."
    else:
        for i in confirmedTeamMembers:
            response += "\n{}. {} - {}".format(i['index'], i['name'], i['team_position'])
        # confirmedTeamMemberIndex+=1

    response += "\n\n> Unconfirmed team members:"
    if len(unconfirmedTeamMembers) < 1:
        response += "\nNone."
    else:
        unconfirmedCount = 1
        for i in unconfirmedTeamMembers:
            response += "\n{}. {} - {}".format(i['index'], i['name'], i['team_position'])

    response += "\n\n> Team members that declined:"

    if len(declinedTeamMembers) < 1:
        response += "\nNone."
    else:
        for i in declinedTeamMembers:
            response += "\n{}. {} - {}".format(i['index'], i['name'], i['team_position'])


    response += "\n\nUse the .update-sunday-team command to confirm member availability."

    await ctx.send(response)

# include command for getting
@bot.command(name="get-songs")
async def get_songs(ctx, date=upcomingSundayList[0]):

    for d in d_getUpcomingSundays['data']:
        date1 = datetime.strptime(d['attributes']['dates'], "%d %B %Y")
        if date == upcomingSundayList[0]:
            date2 = datetime.strptime(date, "%d %B %Y")
        else:
            date2 = datetime.strptime(date, "%b%d")
            

        if date1.strftime("%b%d") == date2.strftime("%b%d"):
            idSelectedSunday = d['id']

    # make request for next Sunday
    getNextSunday = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idSelectedSunday, auth=HTTPBasicAuth(username, password))
    d_getNextSunday = json.loads(getNextSunday.text)

    # get songs for given Sunday
    sundaySongs = []
    getSundaySongs = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idSelectedSunday+'/items', auth=HTTPBasicAuth(username, password))
    d_getSundaySongs = json.loads(getSundaySongs.text)

    for i in range(len(d_getSundaySongs['data'])):
        if d_getSundaySongs['data'][i]['attributes']['item_type'] == 'song':
            sundaySongs.append(i)
    
    # respond to song query for a given Sunday
    songQueryResponse = "{} songs will be played during worship on Sunday {}.\n> Worship".format(
        len(sundaySongs),
        d_getNextSunday['data']['attributes']['dates'])
    for s in range(len(sundaySongs)):
        songQueryResponse += "\n{}. *{}* in the key of {}".format(
            s+1,
            d_getSundaySongs['data'][sundaySongs[s]]['attributes']['title'],
            d_getSundaySongs['data'][sundaySongs[s]]['attributes']['key_name'],
        )

    sundayPerformances = []
    for i in range(len(d_getSundaySongs['data'])):
        if d_getSundaySongs['data'][i]['attributes']['title'].strip() == "Communion" \
        or d_getSundaySongs['data'][i]['attributes']['title'].strip() == "Giving":
            sundayPerformances.append(d_getSundaySongs['data'][i])

    songQueryResponse += "\n\n**Other info**"
    for perf in sundayPerformances:
        songQueryResponse += f"\n> {perf['attributes']['title']}\n{perf['attributes']['description']}"
 

    await ctx.send(songQueryResponse)

@bot.command(name="update-sunday-team")
async def update_sunday_team(ctx, mid: int, status_code, date=upcomingSundayList[0]):
    
    try:
        for d in d_getUpcomingSundays['data']:
            date1 = datetime.strptime(d['attributes']['dates'], "%d %B %Y")
            if date == upcomingSundayList[0]:
                date2 = datetime.strptime(date, "%d %B %Y")
            else:
                date2 = datetime.strptime(date, "%b%d")
                

            if date1.strftime("%b%d") == date2.strftime("%b%d"):
                idSelectedSunday = d['id']

        getSundayTeam = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idSelectedSunday+'/team_members', auth=HTTPBasicAuth(username, password)) # replace the id with idSelectedSunday
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

                updated_member = member

                update = {"data": data}

                url = "https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/{}/team_members/{}".format(idSelectedSunday, member['pc_id']) # replace the id with idSelectedSunday
                print(data)
                print(url)
                r = re.patch(url, json=update, auth=HTTPBasicAuth(username, password))
                # print(r.request.url)
                # print(r.request.body)
                # print(r.request.headers)
                # print(r.status_code)

        if status_code.upper() == "D":
            full_status = "Declined"
        elif status_code.upper() == "U":
            full_status = "Unconfirmed"
        elif status_code.upper() == "C":
            full_status = "Confirmed"

        await ctx.send(f"Status for {updated_member['name']} for {updated_member['team_position']} updated to {full_status}.\n\nHere is the updated team list for Sunday {date1.strftime('%d %B %Y')}")

        await sunday_team(ctx, date)
    except Exception as e:
        
        await owner.send(f"Error occured: {e}")

@bot.command(name="get-arrangments")
async def get_arrangments(ctx, song_name):
    # get the song
    getSong = re.get('https://api.planningcenteronline.com/services/v2/songs?per_page=100', auth=HTTPBasicAuth(username, password))
    d_getSong = json.loads(getSong.text)

    for song in d_getSong['data']:
        if song_name == song['attributes']['title'].strip():
            selected_song = song

    getArrangements = re.get(f"https://api.planningcenteronline.com/services/v2/songs/{selected_song['id']}/arrangements", auth=HTTPBasicAuth(username, password))
    d_getArrangements = json.loads(getArrangements.text)

    # write a dict that contains the various entries for the arrangementResponse.
    # If the entry is Null in the returned JSON (e.g Wo So has no ccli_number) then don't add the entry to arrangementResponse.
    arrangementInfo = {
        0: 'Title',
        1: 'Last scheduled (during worship) on',
        2: 'Songwriter(s)',
        3: 'Copyright',
        4: 'CCLI #',
        5: 'BPM',
        6: 'Meter',
        7: 'Key',
        9: 'Chord chart',
        10: 'Attachments'
    }

    arrangementResponse = f"**Song information for {song_name}.**\n\n"
    arrangementResponse += check_null(selected_song['attributes']['title'], arrangementInfo[0])
    arrangementResponse += check_null(selected_song['attributes']['author'], arrangementInfo[2])
    arrangementResponse += check_null(selected_song['attributes']['copyright'], arrangementInfo[3])
    arrangementResponse += check_null(selected_song['attributes']['ccli_number'], arrangementInfo[4])
    arrangementResponse += check_null(selected_song['attributes']['bpm'], arrangementInfo[5])
    arrangementResponse += check_null(selected_song['attributes']['meter'], arrangementInfo[6])
    arrangementResponse += check_null(selected_song['attributes']['chord_chart_key'], arrangementInfo[7])
    arrangementResponse += check_null(selected_song['attributes']['last_scheduled_short_dates'], arrangementInfo[1])


    # we can get the chord chart, which includes lyrics
    # we can also get the audio for parts if they exist
    # we can also get song info. Perhaps I'll put basic info like bpm, meter and key at the top, and have links to other files later.

@update_sunday_team.error
async def update_sunday_team_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Make sure you put in all the parameters for this command. Send $help command-name-here to get help on a command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{error}; did you type out your command correctly?")

@bot.event
async def on_command_error(ctx, error):
    owner = bot.get_user(442801889986347018)
    if owner is not None:
        await owner.send(f"Command received: {ctx.message.content}\n Error: {error}")
    await ctx.send(f"An error occurred. Help, {owner.mention}!")
    

bot.run(TOKEN)
