from nodeOb import *
fields = {
    "name":nodeOb(nType="String",nTitle="your name",nQuestion="What is your name?",next="email"),
    
    "email":nodeOb(nType="String",nTitle="your email",nQuestion="What is your email address?",next="address"),
    
    "address":nodeOb(nType="String",nTitle="the address you'll be coming from",nQuestion="What is the address you'll be coming from?",next="num_seats"),
    
    "num_seats":nodeOb(nType="Integer",nTitle="the number of seats in your car (0 if you have no car)",nQuestion="How many seats are there in your car? Please input a number; enter 0 if you cannot drive to the event.",next="preWindow",quickChoices={"I don't have a car":'0',"1 seat (only me)":'1',"2 seats total":'2',"3 seats":'3',"4 seats":'4',"5 seats":'5',"6 seats":'6',"7 seats":'7'}),
    
    "preWindow":nodeOb(nType="Integer",nTitle="the earliest you can be ready to go",nQuestion="What is the earliest you can leave your house before the event?",next="on_time",quickChoices={"15 mins before event":'15',"20 mins before event":'20',"25 Minutes":'25',"30 Minutes":'30',"40 Minutes":'40',"45 Minutes":'45',"1 Hour":'60',"1 Hour 15 Minutes":'75'}),
    
    "on_time":nodeOb(nType="Integer",nTitle="your inability to be late (1 or 0)",nQuestion="Do you have to arrive on time? Can you be 30 minutes late? Please answer 1 if you are an organizer of this event or 0 otherwise.",next="must_drive",quickChoices={"Can be a bit late":'0',"Must arrive on time":'1'}),
    
    "must_drive":nodeOb(nType="Integer",nTitle="your REQUIREMENT to drive (1 for \"have to drive\"; 0 for \"don't have to drive\")",nQuestion="Do you have to drive, or is catching a ride an option? Please answer Yes if you have to drive, or No otherwise.",next="menu",quickChoices={"Can drive or ride":'0',"Must drive own car":'1'}),
    
    "menu":nodeOb(nType="String",nTitle="whether you'd like to edit your information",nQuestion="Would you like to edit your information?",next='quick_menu',quickChoices={"All good!":'confirming',"Name":'name',"Email":'email',"Address":'address',"Number of seats":'num_seats',"Drivetime Limit":'preWindow',"Arrival Flexibility":'on_time',"Must drive own car":'must_drive'}),
    
    "confirming":nodeOb(nType="String",nTitle="everything you've entered.",nQuestion="Is all of the following correct?\n{_all}",next='quick_menu',quickChoices={"All correct!":"CREATE_POOL","Need to go back...":'menu'},verboseNode=True)
}
