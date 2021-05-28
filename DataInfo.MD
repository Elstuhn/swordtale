### Data Storage Information
###### Banned 
Dict type. 
key = userid(string), value = Player instance

###### Races
Dict type. 
key = class name(string), value = stats(Dict). 
Stats key = statname(string), value = statvalue(integer)

###### admin
list of admin ids

###### players
Dict type. 
key = userid(string), value = Player instance

###### tinteraction
Dict type. 
key = coordinates(string), value = target(dict). 
Target key = location/npc name(string), value = scene(dict). 
Scene key = action(string), Scene value = interaction(discord.embed)

###### playerlist
list of userids

###### map_
2d array

###### baninfo
Dict type. 
key = playerid(string), value = array [banreason(string), date of ban(datetime obj), bannername(string), bannerid(string)]

###### places
Dict type. Key = coords(string), value = description(string)

###### skills
Dict type. 
key = skillname(string), value = levelUpValues(dict). 
levelUpValues key = levelUpNumber(int), levelUpValues value = array([skillLevelName(string), multiplier(float)])

###### levels
array of required exp to levelup

###### locationinfo
Dict type. 
key = coords(string), value = information(discord.embed)

###### mobs
Dict type. key = mobset id, value = MobSet(dict). MobSet key = mobname(string), MobSet value = mobstats(array)

###### guilds
Dict type.
Key = guildname(string), value = Guild instance