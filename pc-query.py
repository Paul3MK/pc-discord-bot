import requests as re
from requests.auth import HTTPBasicAuth
import json

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
getSundaySongs = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/'+idUpcomingSundays[0]+'/items', auth=HTTPBasicAuth(username, password))
d_getSundaySongs = json.loads(getSundaySongs.text)

for i in range(len(d_getSundaySongs['data'])):
    if d_getSundaySongs['data'][i]['attributes']['item_type'] == 'song':
        sundaySongs.append(i)
    
print(sundaySongs)

# respond to song query for a given Sunday
songQueryResponse = "{} songs will be played on Sunday {}.\nFirst song is {} in the key of {}.\nSecond song is {} in the key of {}\nThird song is {} in the key of {}.".format(
    len(sundaySongs),
    d_getNextSunday['data']['attributes']['dates'],
    d_getSundaySongs['data'][sundaySongs[0]]['attributes']['title'],
    d_getSundaySongs['data'][sundaySongs[0]]['attributes']['key_name'],
    d_getSundaySongs['data'][sundaySongs[1]]['attributes']['title'],
    d_getSundaySongs['data'][sundaySongs[1]]['attributes']['key_name'],
    d_getSundaySongs['data'][sundaySongs[2]]['attributes']['title'],
    d_getSundaySongs['data'][sundaySongs[2]]['attributes']['key_name'],
)

print(songQueryResponse)
# making requests for a given Sunday
# r1 = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/56994712/items', auth=HTTPBasicAuth(username, password))
# r2 = re.get('https://api.planningcenteronline.com/services/v2/service_types/1145804/plans/56994712/', auth=HTTPBasicAuth(username, password))

# d_r1 = json.loads(r1.text)
# d_r2 = json.loads(r2.text)

# songItems = []


# for i in range(len(d_r1['data'])):
#     if d_r1['data'][i]['attributes']['item_type'] == 'song':
#         songItems.append(i)

# songReply = "{} songs will be played on {}.".format(len(songItems), d_r2['data']['attributes']['dates'])

# songSet = "The first song is {} in the key of {}".format(d_r1['data'][8]['attributes']['title'], d_r1['data'][8]['attributes']['key_name'])

# print(songSet)


# print(len(d_r1['data']))
# print(songReply)