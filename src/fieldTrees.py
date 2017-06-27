from nodeOb import nodeOb
from collections import OrderedDict

modesFirst = {'fields':'name','poolfields':'poolName','findPool':'id','tripfields':'address'}

#Custom validator functions here; add them as kwargs as 'validator'
#Custom processor functions here; add them as kwargs as 'processor'
#Possibly import html templates to use in node constructor for webview payload!!! Jinja? Angular? How do those run?

#    "start":nodeOb(nType="String",nTitle="whether this is your information"),

# in psql:
# /c poolchat;
# select engaged, fieldstate, name, email, address, num_seats, on_time, must_drive, menu, confirming, "preWindow", "fbId" from carpooler;

fields = {
	"name":nodeOb(nType="String",fieldname='name',nTitle="your name",next="email",nodeName="Name",obField="Carpooler"),

	"email":nodeOb(nType="String",fieldname='email',nTitle="your email, {name}",obField="Carpooler",next="menu",nodeName="Email",verboseNode=True),

	"menu":nodeOb(nType="String",fieldname='menu',nTitle="whether you'd like to edit your information",nQuestion="Would you like to change the following?\n{_all}",next='quick_menu',quickChoices=OrderedDict([("All good!",'mode'),("Name",'name'),("Email",'email')]),verboseNode=True,obField='Carpooler'),

	"mode":nodeOb(nType="String",fieldname='mode',nTitle="everything you've entered",nQuestion="What would you like to do now?\n{_all}",next='quick_menu',quickChoices=OrderedDict([("Create NEW carpool","CREATE_NEW_POOL"),("JOIN a carpool","SWITCH_MODE/findPool"),("Need to go back..",'menu')]),verboseNode=True,obField='Carpooler')

	# "mode":nodeOb(nType="String",nTitle="everything you've entered.",nQuestion="Is all of the following correct?\n{_all}",next='quick_menu',quickChoices={"Create NEW carpool":"poolfields","JOIN a carpool":"findPool","Need to go back...":'menu'},verboseNode=True,obField='Carpooler')
}


findPool = {
				"id":nodeOb(nType="String",fieldname='id',nTitle="the ID of the pool you're looking for",nQuestion="What is the ID of the pool you'd looking for?\n{tripstring}",next='quick_menu',quickChoices={"Create NEW carpool":"CREATE_NEW_POOL"},prefix= "FIND_POOL/",validator = (lambda input: True),verboseNode = True,nodeName="Pool ID",obField='findPool'),

				"mode":nodeOb(nType="String",fieldname='mode',nTitle="everything you've entered.",nQuestion="Is all of the following correct?\n{_all}",next='quick_menu',quickChoices=OrderedDict([("Create NEW carpool","poolfields"),("JOIN a carpool","findPool")]),verboseNode=True,obField='findPool')
}


#NOTE: need an 'altchoices' node type, for when different choices lead to different next nodes. Or maybe just add functionality for when there is "quickchoices" and "nextchoices" listed!
poolfields = {
	"poolName":nodeOb(nType="String",fieldname='poolName',nTitle="the name of the event you'll be going to",next="eventDate",nodeName="Event Address",obField='Pool'),

	"eventDate":nodeOb(nType="String",fieldname='eventDate',nTitle="the date of your event",next="eventTime",nodeName="Event Date",obField='Pool'),

	"eventTime":nodeOb(nType="String",fieldname='eventTime',nTitle="the time your event starts on {eventDate}",next="eventAddress",nodeName="Event Time",verboseNode=True,obField='Pool'),

	"eventAddress":nodeOb(nType="String",fieldname='eventAddress',nTitle="the address you'll be going to",prefix='FIND_ADDRESS/',next="addressMenu",nodeName="Event Address",obField='Pool'),

	"addressMenu":nodeOb(nType="String",fieldname='addressMenu',nTitle="whether that address is correct",nQuestion="Would you like to change the address you entered?\nAddress: {eventAddress}",next='quick_menu',quickChoices=OrderedDict([("Change it",'eventAddress'),("That's fine","eventContact")]),verboseNode=True,prefix="GOTO_NODE/",obField='Pool'),

	"eventContact":nodeOb(nType="String",fieldname='eventContact',nTitle="the phone number of someone organizing this event",next="eventEmail",nodeName="Event Contact",obField='Pool'),

	"eventEmail":nodeOb(nType="String",fieldname='eventEmail',nTitle="the email address of someone organizing this event",next="eventHostOrg",nodeName="Event Email",obField='Pool'),

	"eventHostOrg":nodeOb(nType="String",fieldname='eventHostOrg',nTitle="the name of the organization that is organizing this event",next="signature",nodeName="Event Host Org",obField='Pool'),


	"signature":nodeOb(nType="String",fieldname='signature',nTitle="how you'd like to sign messages about this event",nQuestion="How would you like to sign messages about this event?\nClick 'Default' to sign with 'Looking forward to seeing you there!' or 'Blank' to omit a signature.",next='latenessWindow',nodeName="Signature",quickChoices=OrderedDict([("Default","Looking forward to seeing you there!"),("Blank","")]),obField='Pool'),

	"latenessWindow":nodeOb(nType="String",fieldname='latenessWindow',nTitle="arrival time flexibility for this event",nQuestion="Can people attending this event arrive a bit late? Organizers need to arrive on time at {eventTime}, but can others arrive a bit later if necessary?",next='fireTime',verboseNode=True,nodeName="Arrival Time Flexibility",quickChoices=OrderedDict([("No - come on time","0"),("15 Minutes","15"),("30 Minutes","30"),("45 Minutes","45"),("1 hour","60")]),obField='Pool'),

	"fireTime":nodeOb(nType="String",fieldname='fireTime',nTitle="when instructions should be calculated and sent out",nQuestion="The event at {eventAddress} starts at {eventTime} on {eventDate}. When should GroupThere close the event, calculate carpools, and send out instructions to all attendees?",nodeName="Instruction Notice (hours before event)",verboseNode=True,next='menu',quickChoices=OrderedDict([("6 hours before","6"),("12 hours before","12"),("1 day before","24"),("36 hours before","36"),("2 days before","48"),("1 week before","168")]),obField='Pool'),


	"menu":nodeOb(nType="String",fieldname='menu',nTitle="whether you'd like to edit your information",nQuestion="Would you like to change the following?\n{_all}",next='quick_menu',quickChoices=OrderedDict([("All good!",'mode'),('Event Name','MENU_RETURN/poolName'),("Date",'MENU_RETURN/eventDate'),("Time",'MENU_RETURN/eventTime'),("Address",'MENU_RETURN/eventAddress'),("Contact",'MENU_RETURN/eventContact'),("Email",'MENU_RETURN/eventEmail'),("Host Org",'MENU_RETURN/eventHostOrg'),("Signature",'MENU_RETURN/signature'),("Arrival Flexibility",'MENU_RETURN/latenessWindow'),("Instruction Notice",'MENU_RETURN/fireTime')]),verboseNode=True,obField='Pool'),

	"mode":nodeOb(nType="String",fieldname='mode',nTitle="everything you've entered.",nQuestion="Is all of the following correct?\n{_all}",next='quick_menu',quickChoices=OrderedDict([("Yes, I want to go!","SWITCH_MODE/tripfields"),("Need to edit event..","menu")]),verboseNode=True,obField='Pool')
}


tripfields = {

	"address":nodeOb(nType="String",fieldname='address',nTitle="the address you'll be coming from",nQuestion="I know your personal information (email, name) and about your event, but I need to know about how you'll get there.\n\nWhat is the address you'll be coming from?\n (I know you'll be going TO {pool_eventAddress})",prefix='FIND_ADDRESS/',verboseNode=True,next="addressMenu",nodeName="Address",obField='Trip'),

	"addressMenu":nodeOb(nType="String",fieldname='addressMenu',nTitle="whether that address is correct",nQuestion="Would you like to change the address you entered?\nAddress: {pool_eventAddress}",next='quick_menu',quickChoices={"Change it":'address',"That's fine":"num_seats"},verboseNode=True,prefix="GOTO_NODE/",obField='Trip'),

	"num_seats":nodeOb(nType="Integer",fieldname='num_seats',nTitle="the number of seats in your car",nQuestion="How many seats are there in your car?",next="preWindow",quickChoices=OrderedDict([("I don't have a car",'0'),("1 seat (only me)",'1'),("2 seats total",'2'),("3 seats",'3'),("4 seats",'4'),("5 seats",'5'),("6 seats",'6'),("7 seats",'7')]),nodeName="Number of Seats",obField='Trip'),

	"preWindow":nodeOb(nType="Integer",fieldname='preWindow',nTitle="the earliest you can be ready to go",nQuestion="What is the earliest you can leave before the event at {pool_eventAddress}, at {pool_eventTime}?\n(You will be coming from {address})",next="on_time",quickChoices=OrderedDict([("15 mins before event",'15'),("20 mins before event",'20'),("25 Minutes",'25'),("30 Minutes",'30'),("40 Minutes",'40'),("45 Minutes",'45'),("1 Hour",'60'),("1 Hour 15 Minutes",'75')]),verboseNode=True,nodeName="Minutes Available for Transit",obField='Trip'),

	"on_time":nodeOb(nType="Integer",fieldname='on_time',nTitle="your inability to be late (1 or 0)",nQuestion="Do you have to arrive on time? Can you be 30 minutes late? (If you are an organizer of the event, you have to arrive on time)",next="must_drive",quickChoices={"Can be a bit late":'0',"Must arrive on time":'1'},nodeName="Have to Arrive on Time",obField='Trip'),

	"must_drive":nodeOb(nType="Integer",fieldname='must_drive',nTitle="your REQUIREMENT to drive",nQuestion="Do you have to drive, or is catching a ride an option?",next="menu",quickChoices={"Can drive or ride":'0',"Must drive own car":'1'},nodeName="Have to Drive Self",obField='Trip'),
	#NEED RESPONSE/Trip prefix here??!?
	"menu":nodeOb(nType="String",fieldname='menu',nTitle="whether you'd like to edit your information",nQuestion="Would you like to change the following?\n{_all}",next='quick_menu',quickChoices=OrderedDict([("All good!",'mode'),("Origin Address",'MENU_RETURN/address'),("Number of seats",'MENU_RETURN/num_seats'),("Drivetime Limit",'MENU_RETURN/preWindow'),("Arrival Flexibility",'MENU_RETURN/on_time'),("Must drive own car",'MENU_RETURN/must_drive'),("Traveler Info","SWITCH_MODE/fields")]),verboseNode=True,obField='Trip'),

	"mode":nodeOb(nType="String",fieldname='mode',nTitle="everything you've entered.",nQuestion="What would you like to do now?",quickChoices=OrderedDict([("Create NEW carpool","CREATE_NEW_POOL"),("JOIN a carpool","findPool"),("Need to go back...",'menu')]),verboseNode=True,obField='Trip')




}
