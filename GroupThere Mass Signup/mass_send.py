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
# users = [{'email':'grouptheretest@gmail.com','first':'Zach','last':'Siegel'}]
filein = open('signups.csv', 'r')
bash_filename = 'signups.sh'
reader = csv.reader(filein)
headers = next(reader, None)
users = [{headers[i] : row[i] for i in range(len(headers)) if ((row[i] is not None) and (row[i] is not ''))} for row in reader]

fileout = open(bash_filename,'w')


## PROCESS

print("\n\n\n\n\nheroku run bash --app {};\n\n\n\n".format(app))

cmd = "cd src;"

for user in users:
    info={}
    if teamid is not None:
        info['teamidPart'] = " --teamid '{}'".format(teamid)
    if eventid is not None:
        info['eventidPart'] = " --eventid '{}'".format(eventid)
    if user.get('first') is not None:
        info['firstPart'] = " --first '{}'".format(user['first'])
    if user.get('last') is not None:
        info['lastPart'] = " --last '{}'".format(user['last'])

    cmd += " python manage.py generate_oneclick --email '{}'{}{}{}{};".format(user['email'],info.get('teamidPart') or '',info.get('eventidPart') or '',info.get('firstPart') or '',info.get('lastPart') or '')


fileout.write("heroku run bash -c \"{}\" --app {};\n\n".format(cmd, app))

print("\n\nheroku run bash -c \"{}\" --app {};\n\n".format(cmd, app))
print(f'\n\nUse:\n\nsh {bash_filename}\n\n')
filein.close()
fileout.close()
