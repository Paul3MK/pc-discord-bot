from http import client
import os
from select import select
# from termios import ECHOE
from urllib.error import HTTPError
import discord
from dotenv import load_dotenv

from discord.ext import commands

import requests as re
from requests.auth import HTTPBasicAuth
import json

from datetime import datetime
import attachment as at
import logging
logging.basicConfig(level=logging.DEBUG)


# getting relevant data from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# setting intents for Discord
intents = discord.Intents.default()
intents.members = True

activity = discord.Game(name=".help for commands.")
bot = commands.Bot(command_prefix='.', intents=intents, activity=activity)

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
        return ""

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

@bot.command(name="roast", help="Use this command to critique me!")
async def roast(ctx, *, roasting):
    async with ctx.typing():
        owner = bot.get_user(442801889986347018)
        if owner is not None:
            await owner.send(f"I was roasted! {roasting}")

    await ctx.send("😭 Thanks for the feedback!")

@bot.command(name="upcoming-sundays", help="Get the upcoming planned Sundays.")
async def upcoming_sundays(ctx):
    dates = []
    for i in d_getUpcomingSundays["data"]:
        dates.append(i["attributes"]["dates"])

    response = "Here are the upcoming Sundays that have complete plans: "

    for date in dates:
        response += f"\n{date}"
    
    await ctx.send(response)

@bot.command(name="next-sunday-info", help="Get song and team info for next Sunday.") # not implemented yet
async def next_sunday_info(ctx):
    await sunday_team(ctx)
    await get_songs(ctx)

@bot.command(name="sunday-team", help="Gets the list of team members for a given Sunday.")
async def sunday_team(ctx, date=upcomingSundayList[0]):
    async with ctx.typing():
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

        response = f"**Current team status for Sunday {date2.strftime('%d %B')}:**\n"

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


        response += "\n\nUse the .update-sunday-team command to modify member availability."

        await ctx.send(response)

# include command for getting
@bot.command(name="get-songs", help="Gets songs for a given Sunday.")
async def get_songs(ctx, date=upcomingSundayList[0]):
    async with ctx.typing():
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
        songQueryResponse = "**Song Details**\n{} songs will be played during worship on Sunday {}.\n> Worship".format(
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

@bot.command(name="update-sunday-team", help="Update team statuses for a given Stunday.")
async def update_sunday_team(ctx, mid: int, status_code, date=upcomingSundayList[0]):
    async with ctx.typing():
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

            await ctx.send(f"Status for {updated_member['name']} for {updated_member['team_position']} updated to {full_status}.\n\nHere is the updated team list for Sunday {date2.strftime('%d %B %Y')}")

            await sunday_team(ctx, date)
        except Exception as e:
            
            await owner.send(f"Error occured: {e}")

@bot.command(name="get-all-arrangements", help="Get the full list of songs in Planning Center.")
async def get_all_arrangments(ctx):
    async with ctx.typing():
        getAllSongs = re.get('https://api.planningcenteronline.com/services/v2/songs?per_page=100', auth=HTTPBasicAuth(username, password))
        d_getAllSongs = json.loads(getAllSongs.text)

        songList = []

        for song in d_getAllSongs['data']:
            songList.append(song['attributes']['title'])

    printedSongList = "> Here's the full list of songs in the Planning Center Services database:\n"
    for s in songList:
        printedSongList += f"{s}\n"
    
    await ctx.send(printedSongList)

@bot.command(name="get-arrangement", help="Get arrangement info for a given song.")
async def get_arrangement(ctx, *, song_name):
    async with ctx.typing():
        getSong = re.get('https://api.planningcenteronline.com/services/v2/songs?per_page=100', auth=HTTPBasicAuth(username, password))
        d_getSong = json.loads(getSong.text)

        for song in d_getSong['data']:
            temp = song['attributes']['title'].strip()
            if song_name[0:9] == temp[0:9]:
                selected_song = song

        getArrangements = re.get(f"https://api.planningcenteronline.com/services/v2/songs/{selected_song['id']}/arrangements?include=keys", auth=HTTPBasicAuth(username, password))
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
            8: 'Arrangement by',
            9: 'Chord chart',
            10: 'Attachments'
        }

        arrangementResponse = f"**Song information for {selected_song['attributes']['title']}.**\n\n"
        arrangementResponse += check_null(selected_song['attributes']['title'], arrangementInfo[0])
        arrangementResponse += check_null(d_getArrangements['data'][0]['attributes']['name'], arrangementInfo[8])
        arrangementResponse += check_null(selected_song['attributes']['author'], arrangementInfo[2])
        # arrangementResponse += check_null(selected_song['attributes']['copyright'], arrangementInfo[3])
        arrangementResponse += check_null(selected_song['attributes']['ccli_number'], arrangementInfo[4])
        arrangementResponse += check_null(d_getArrangements['data'][0]['attributes']['bpm'], arrangementInfo[5])
        arrangementResponse += check_null(d_getArrangements['data'][0]['attributes']['meter'], arrangementInfo[6])
        arrangementResponse += check_null(d_getArrangements['data'][0]['attributes']['chord_chart_key'], arrangementInfo[7])
        arrangementResponse += check_null(selected_song['attributes']['last_scheduled_short_dates'], arrangementInfo[1])

        if d_getArrangements['included'][0]['id'] is not None:
            key_id = d_getArrangements['included'][0]['id']
            arr_id = d_getArrangements['data'][0]['id']

        getChordChart = re.post(f"https://api.planningcenteronline.com/services/v2/songs/{selected_song['id']}/arrangements/{arr_id}/keys/{key_id}/attachments/chord_chart-{key_id}--/open", auth=HTTPBasicAuth(username, password))
        d_getChordChart = json.loads(getChordChart.text)

        try:
            chordChartURL = d_getChordChart['data']['attributes']['attachment_url']
            arrangementResponse += f"{arrangementInfo[9]}: ||{chordChartURL}||"
        except Exception:
            pass


    await ctx.send(arrangementResponse)


    # we can get the chord chart, which includes lyrics
    # we can also get the audio for parts if they exist
    # we can also get song info. Perhaps I'll put basic info like bpm, meter and key at the top, and have links to other files later.

@bot.command(name="get-mixes", help="Gets the band mixes for a given song.")
async def get_mixes(ctx, *, song_name):
    async with ctx.typing():
        band_mixes = at.get_mixes(song_name[0:9])
        mix_output = ""

        if band_mixes is not HTTPError:
            if type(band_mixes) is not str:
                for mix in band_mixes:
                    mix_output += f"{mix}\n"
            else:
                mix_output = "I couldn't find any band mixes for this song."
        else:
            mix_output = "An error occurred; Google Drive cannot be accessed at this time."

        mix_output += "\nDone!"
        await ctx.send(mix_output)

# @update_sunday_team.error
# async def update_sunday_team_error(ctx, error):
#     if isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send("Make sure you put in all the parameters for this command. Send .help command-name-here to get help on a command.")
#     elif isinstance(error, commands.CommandNotFound):
#         await ctx.send(f"{error}; did you type out your command correctly?")

# @get_arrangements.error
# async def get_arrangements_error(ctx, error):
#     if isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send("Make sure you put in all the parameters for this command. Send .help command-name-here to get help on a command.")
#     elif isinstance(error, commands.CommandNotFound):
#         await ctx.send(f"{error}; did you type out your command correctly?")

@bot.event
async def on_command_error(ctx, error):
    owner = bot.get_user(442801889986347018)
    if owner is not None:
        await owner.send(f"Command received: {ctx.message.content}\n Error: {error}")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Make sure you put in all the parameters for this command. Send .help command-name-here to get help on a command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{error}; did you type out your command correctly?")
    else:
        await ctx.send(f"An error occurred. Help, {owner.mention}!")
    

bot.run(TOKEN)
