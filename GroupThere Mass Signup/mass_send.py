#To use this script:
# 1. Choose app
# 2. Change the 'users' dict to contain everyone's info.,change teamid,eventid
# 3. Run script
# 4. Copy and paste commands into terminal from ~/poolchat to have REAL invitation emails sent.
# Commands are like:
# python manage.py generate_oneclick --email 'grouptheretest@gmail.com' --teamid '1' --eventid '2' --first 'Zach' --last 'Siegel';
import csv

## PARAMS

# app = 'groupthere'
app = 'groupthere-stage'
teamid='1'
eventid='11'
message = "Hey all, check this out! I am sending a message!"
# users = [{'email':'grouptheretest@gmail.com','first':'Zach','last':'Siegel'}]
# filename = 'Tribe_Retreat_Contact_Formatted.csv'
# filename = 'signups.csv'
filename= "/Users/Zach/poolchat/mass_signup_dump/signups.csv"
filein = open(filename, 'r')
filepath = filename.split('/')
bash_filename = "/".join(filepath[:-1] + ['contact__' + ".".join(filepath[-1].split(".")[:-1]) + '.sh'])
reader = csv.reader(filein)
headers = next(reader, None)
users = [{headers[i] : row[i] for i in range(len(headers)) if ((row[i] is not None) and (row[i] is not ''))} for row in reader]

fileout = open(bash_filename,'w')


## PROCESS

cmd = "cd src;"

for user in users:
    info={}
    if teamid is not None:
        info['teamidPart'] = " --teamid '{}'".format(teamid)
    if eventid is not None:
        info['eventidPart'] = " --eventid '{}'".format(eventid)
    if message is not None:
        info['messagePart'] = " --message '{}'".format(message)
    if user.get('first') is not None:
        info['firstPart'] = " --first '{}'".format(user['first'])
    if user.get('last') is not None:
        info['lastPart'] = " --last '{}'".format(user['last'])
    cmd += " python manage.py generate_oneclick --email '{}'{}{}{}{}{};".format(user['email'],info.get('teamidPart') or '',info.get('eventidPart') or '',info.get('firstPart') or '',info.get('lastPart') or '',info.get('messagePart') or '')

cmd = "heroku run bash -c \"{}\" --app {};\n\n".format(cmd, app)
fileout.write(cmd)

print(cmd)
print(f'\n\nUse:\n\nsh {bash_filename}\n\n')
filein.close()
fileout.close()
