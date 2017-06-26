from nodeOb import nodeOb

modesFirst = {'fields':'name','poolfields':'eventAddress','findPool':'id','tripfields':'address'}

#Custom validator functions here; add them as kwargs as 'validator'
#Custom processor functions here; add them as kwargs as 'processor'
#Possibly import html templates to use in node constructor for webview payload!!! Jinja? Angular? How do those run?

#    "start":nodeOb(nType="String",nTitle="whether this is your information"),

# in psql:
# /c poolchat;
# select engaged, fieldstate, name, email, address, num_seats, on_time, must_drive, menu, confirming, "preWindow", "fbId" from carpooler;

fields = {
	"name":nodeOb(nType="String",fieldname='name',nTitle="your name",nQuestion="What is your name?",next="email",nodeName="Name",obField="Carpooler"),

	"email":nodeOb(nType="String",fieldname='email',nTitle="your email",obField="Carpooler",nQuestion="What is your email address, {name}?",next="menu",nodeName="Email",verboseNode=True),

	"menu":nodeOb(nType="String",fieldname='menu',nTitle="whether you'd like to edit your information",nQuestion="Would you like to change the following?\n{_all}",next='quick_menu',quickChoices={"All good!":'mode',"Name":'name',"Email":'email'},verboseNode=True,obField='Carpooler'),

	"mode":nodeOb(nType="String",fieldname='mode',nTitle="everything you've entered",nQuestion="What would you like to do now?\n{_all}",next='quick_menu',quickChoices={"Create NEW carpool":"CREATE_NEW_POOL","JOIN a carpool":"SWITCH_MODE/findPool","Need to go back..":'menu'},verboseNode=True,obField='Carpooler')

	# "mode":nodeOb(nType="String",nTitle="everything you've entered.",nQuestion="Is all of the following correct?\n{_all}",next='quick_menu',quickChoices={"Create NEW carpool":"poolfields","JOIN a carpool":"findPool","Need to go back...":'menu'},verboseNode=True,obField='Carpooler')
}


findPool = {
				"id":nodeOb(nType="String",fieldname='id',nTitle="the ID of the pool you're looking for",nQuestion="What is the ID of the pool you'd looking for?\n{tripstring}",next='quick_menu',quickChoices={"Create NEW carpool":"CREATE_NEW_POOL"},prefix= "FIND_POOL/",validator = (lambda input: True),verboseNode = True,nodeName="Pool ID",obField='findPool'),
				"FIND":nodeOb(nType="Integer",fieldname='Find',nTitle="the ID of the pool you're looking for",nQuestion="What is the ID of the pool you'd looking for?",next="mode",nodeName="Pool ID",obField='findPool'),
				"SWITCH":nodeOb(nType="Integer",fieldname='SWITCH',nTitle="the ID of the pool you're looking for",nQuestion="What is the ID of the pool you'd looking for?",next="mode",nodeName="Pool ID",obField='findPool'),
				"mode":nodeOb(nType="String",fieldname='mode',nTitle="everything you've entered.",nQuestion="Is all of the following correct?\n{_all}",next='quick_menu',quickChoices={"Create NEW carpool":"poolfields","JOIN a carpool":"findPool"},verboseNode=True,obField='findPool')
}


#NOTE: need an 'altchoices' node type, for when different choices lead to different next nodes. Or maybe just add functionality for when there is "quickchoices" and "nextchoices" listed!
poolfields = {

	"eventAddress":nodeOb(nType="String",fieldname='eventAddress',nTitle="the address you'll be going to",nQuestion="What is the address you'll be going to?",prefix='FIND_ADDRESS/',next="addressMenu",nodeName="Event Address",obField='Pool'),

	"addressMenu":nodeOb(nType="String",fieldname='addressMenu',nTitle="whether that address is correct",nQuestion="Would you like to change the address you entered?\nAddress: {eventAddress}",next='quick_menu',quickChoices={"Change it":'eventAddress',"That's fine":"eventTime"},verboseNode=True,prefix="GOTO_NODE/",obField='Pool'),

	"eventTime":nodeOb(nType="String",fieldname='eventTime',nTitle="the time of your event",nQuestion="What is the time your event starts?",next="menu",nodeName="Event Time",verboseNode=True,obField='Pool'),

	"menu":nodeOb(nType="String",fieldname='menu',nTitle="whether you'd like to edit your information",nQuestion="Would you like to change the following?\n{_all}",next='quick_menu',quickChoices={"All good!":'mode',"Address":'eventAddress',"Time":'eventTime'},verboseNode=True,obField='Pool'),

	"mode":nodeOb(nType="String",fieldname='mode',nTitle="everything you've entered.",nQuestion="Is all of the following correct?\n{_all}",next='quick_menu',quickChoices={"Yes, I want to go!":"SWITCH_MODE/tripfields","Need to edit event..":"menu"},verboseNode=True,obField='Pool')
}


tripfields = {

"address":nodeOb(nType="String",fieldname='address',nTitle="the address you'll be coming from",nQuestion="Now I know your personal information and about your event.\nWhat is the address you'll be coming from?\n (I know you'll be going TO {pool_eventAddress})",verboseNode=True,next="num_seats",nodeName="Address",obField='Trip'),

	"num_seats":nodeOb(nType="Integer",fieldname='num_seats',nTitle="the number of seats in your car (0 if you have no car)",nQuestion="How many seats are there in your car? Please input a number; enter 0 if you cannot drive to the event.",next="preWindow",quickChoices={"I don't have a car":'0',"1 seat (only me)":'1',"2 seats total":'2',"3 seats":'3',"4 seats":'4',"5 seats":'5',"6 seats":'6',"7 seats":'7'},nodeName="Number of Seats",obField='Trip'),

	"preWindow":nodeOb(nType="Integer",fieldname='preWindow',nTitle="the earliest you can be ready to go",nQuestion="What is the earliest you can leave your house before the event at {pool_eventAddress}?",next="on_time",quickChoices={"15 mins before event":'15',"20 mins before event":'20',"25 Minutes":'25',"30 Minutes":'30',"40 Minutes":'40',"45 Minutes":'45',"1 Hour":'60',"1 Hour 15 Minutes":'75'},verboseNode=True,nodeName="Minutes Available for Transit",obField='Trip'),

	"on_time":nodeOb(nType="Integer",fieldname='on_time',nTitle="your inability to be late (1 or 0)",nQuestion="Do you have to arrive on time? Can you be 30 minutes late? Please answer 1 if you are an organizer of this event or 0 otherwise.",next="must_drive",quickChoices={"Can be a bit late":'0',"Must arrive on time":'1'},nodeName="Have to Arrive on Time",obField='Trip'),

	"must_drive":nodeOb(nType="Integer",fieldname='must_drive',nTitle="your REQUIREMENT to drive (1 for \"have to drive\"; 0 for \"don't have to drive\")",nQuestion="Do you have to drive, or is catching a ride an option? Please answer Yes if you have to drive, or No otherwise.",next="menu",quickChoices={"Can drive or ride":'0',"Must drive own car":'1'},nodeName="Have to Drive Self",obField='Trip'),
	#NEED RESPONSE/Trip prefix here??!?
	"menu":nodeOb(nType="String",fieldname='menu',nTitle="whether you'd like to edit your information",nQuestion="Would you like to change the following?\n{_all}",next='quick_menu',quickChoices={"All good!":'mode',"Origin Address":'address',"Number of seats":'num_seats',"Drivetime Limit":'preWindow',"Arrival Flexibility":'on_time',"Must drive own car":'must_drive',"Traveler Info":"SWITCH_MODE/fields","Carpool Info":"SWITCH_MODE/poolfields"},verboseNode=True,obField='Trip'),

	"mode":nodeOb(nType="String",fieldname='mode',nTitle="everything you've entered.",nQuestion="What would you like to do now?",quickChoices={"Create NEW carpool":"CREATE_NEW_POOL","JOIN a carpool":"findPool","Need to go back...":'menu'},verboseNode=True,obField='Trip')




}
