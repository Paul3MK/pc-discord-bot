import requests as re
from requests.auth import HTTPBasicAuth
import json
import discord
import os

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


# make request for next Sunday
getNextSunday = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idUpcomingSundays[0], auth=HTTPBasicAuth(username, password))
d_getNextSunday = json.loads(getNextSunday.text)

# make a request for a week from next Sunday

# get songs for any Sunday
sundaySongs = []
getSundayItems = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idUpcomingSundays[0]+'/items', auth=HTTPBasicAuth(username, password))
d_getSundayItems = json.loads(getSundayItems.text)

# getting song category
songItem = {
    
}

for i in range(len(d_getSundayItems['data'])):
    if d_getSundayItems['data'][i]['attributes']['item_type'] == 'song' \
        or d_getSundayItems['data'][i]['attributes']['description'] == 'Worship' \
        or d_getSundayItems['data'][i]['attributes']['description'] == 'Communion' \
        or d_getSundayItems['data'][i]['attributes']['description'] == 'Giving': { # YES, this is a huge ORed if statement

        sundaySongs.append(d_getSundayItems['data'][i])
    }
        
    
print(sundaySongs)

# respond to song query for a given Sunday
songCount = 0
for item in sundaySongs:
    if item['attributes']['item_type'] == 'song':
        songCount += 1

songQueryResponse = "{} songs will be played on Sunday {}.".format(
    songCount,
    d_getNextSunday['data']['attributes']['dates'])
for s in sundaySongs:
    songQueryResponse += "\n{}. {} in the key of {}".format(
        s+1,
        d_getSundayItems['data'][sundaySongs[s]]['attributes']['title'],
        d_getSundayItems['data'][sundaySongs[s]]['attributes']['key_name'],
    )

print(songQueryResponse)


# get all team members, grouped by confirmed and unconfirmed
getTeamMembers =  re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idUpcomingSundays[0]+'/team_members', auth=HTTPBasicAuth(username, password))
d_getTeamMembers = json.loads(getTeamMembers.text)

confirmedTeamMembers = []
unconfirmedTeamMembers = []


for i in range(len(d_getTeamMembers['data'])):
    teamMember = {
        "index": i+1,
        "pc_id": "",
        "name": "",
        "team_position": "",
        "status": ""

    }
    if d_getTeamMembers['data'][i]['attributes']['status'] == 'C':
        teamMember['pc_id'] = d_getTeamMembers['data'][i]['id']
        teamMember['name'] = d_getTeamMembers['data'][i]['attributes']['name']
        teamMember['team_position'] = d_getTeamMembers['data'][i]['attributes']['team_position_name']
        teamMember['status'] = d_getTeamMembers['data'][i]['attributes']['status']
        confirmedTeamMembers.append(teamMember)
    elif d_getTeamMembers['data'][i]['attributes']['status'] == 'U':
        teamMember['pc_id'] = d_getTeamMembers['data'][i]['id']
        teamMember['name'] = d_getTeamMembers['data'][i]['attributes']['name']
        teamMember['team_position'] = d_getTeamMembers['data'][i]['attributes']['team_position_name']
        teamMember['status'] = d_getTeamMembers['data'][i]['attributes']['status']
        unconfirmedTeamMembers.append(teamMember)

# print out confirmed team members
print("\nConfirmed team members:")

confirmedTeamMemberIndex = 1

for i in confirmedTeamMembers:
    print("{}. {} - {}".format(i['index'], i['name'], i['team_position']))
    # confirmedTeamMemberIndex+=1

# print out unconfirmed team members
print("\nUnconfirmed team members:")

for i in unconfirmedTeamMembers:
    print("{}. {} - {}".format(i['index'], i['name'], i['team_position']))

# update status for a given team member for a given Sunday
