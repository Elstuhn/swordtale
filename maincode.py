#make storage unit for adventure cards for adventurers guilds
import discord
import time
import typing as t
from time import sleep
import os
import pickle
import asyncio
import random
from discord.ext import commands, tasks
from datetime import datetime
from collections import defaultdict
#calculate function so that damage values can be changed in the middle of battle 
fileopened = {}
''''
Things to note:
-For skills, dont make boosts too high
-For mobs, dont make stats too high (physatk, phys_def, magatk, magdef)
'''
class Player(): #Player Class
    def __init__(self, username, race):
        self.user = username
        self.race = race
        self.inventory = defaultdict(int) #(key=class_instance, value = amount)
        self.gear = {"weapon" : None, "secondary" : None, "helmet" : None, "chest" : None, "legs" : None, "boots" : None, "ring" : None, "amulet" : None, "special" : None}
        self.gold = 0
        self.level = 0
        self.exp = 0
        self.guild = None
        self.guildpos = None
        self.guildins = None
        self.party = None    #party instance
        self.statsp = {'maxhp' : 20, 'agility' : 0, 'atk': 0, 'defense' : 0, 'phys_atk' : 0, 'phys_def' : 0, 'mag_def' : 0, 'mag_atk' : 0, 'looting' : 0, 'cooldown_speed' : 0}
        self.stats = {'maxhp' : 20, 'hp' : 20, 'agility' : 1, 'atk': 5, 'defense' : 2, 'phys_atk' : 1, 'phys_def' : 1, 'mag_def' : 1, 'mag_atk' : 1, 'looting' : 0, 'cooldown_speed' : 0}
        self.class_ = None
        self.skills = {"e" : [0, 0, 'Beginner', 'punch', 1, 1, {}, 5]} #index 0: times used, index 1: level, index 2: level name, index 3: skill name, 4: phy_atk multiplier, 5: mag_atk multiplier 6: {'buffname' : [seconds, {'buffs'('statname': percentage)}]} 7: cooldown time(seconds)
        self.location = ["4-4", "Agelock Town - It seems like time slows down in this town?"]
        self.fightstat = [None, 1] #In fight (if not, None, else, True) index 1 shows if dead or not (1 = alive, 0 = ded)
        self.status = "Adventurer"
        self.advcard = None
        self.quests = {}

class Adventurers_Guild():
    '''
    Adventurer's Guild for adventurers to get quests and get gold and rewards for completing them
    questlist has to be randomized every 12 hours as well with a limit of 8 quests
    '''
    def __init__(self, questlist):
        self.questlist = questlist
        self.members = {}
        
    def register(self, playerins):
        card = Adventurers_Card(playerins.user)
        playerins.advcard = card
        self.members[str(playerins.author.id)] = card
    
    def givequest(self, playerins):
        ## MARK: - TODO
        pass


class Party():
    def __init__(self, owner):
        self.owner = owner
        self.members = [owner] #list will be full of player id in str
        
    def checkdead(self):
        out = True #if out is false at the end, not all dead
        for i in self.members:
            playerins = players[i]
            if playerins.stats['hp'] >= 1:
                out = False
        return out

class Role():
    def __init__(self, name, position, kickPerms = False, invitePerms = False, setrolePerms = False, rolecreationPerms = False, editPerms = False):
        self.name = name
        self.kickPerms = kickPerms
        self.invitePerms = invitePerms
        self.setrolePerms = setrolePerms
        self.rolecreationPerms = rolecreationPerms
        self.editPerms = editPerms
        self.pos = position

class Guild():
    def __init__(self, name : str, owner : str):
        self.name = name
        self.owner = owner # ctx.author.id in str form
        self.value = data.chooseobj('players')[f'{owner}'].gold #set initial guild value to owner's gold amount
        self.members = {} #memberid : membername
        self.roles = {'Guild Master' : guildmaster, 'Member' : member}
        self.rolepos = ['Guild Master', 0, 0, 0, 0, 0, 'Member']

class Mob():
    def __init__(self, name, level, atk, hp, defense, phys_atk, phys_def, mag_atk, mag_def, cooldown_speed, multiplier): #atk, defense, hp will be calculated as constant*multiplier
        self.name = name
        self.level = level
        self.atk = atk
        self.hp = hp
        self.defense = defense
        self.phys_atk = phys_atk
        self.phys_def = phys_def
        self.mag_atk = mag_atk
        self.mag_def = mag_def
        self.cooldown = cooldown_speed
        self.multiplier = multiplier

                 
class Adventurers_Card():
    def __init__(self, user):
        self.owner = user
        self.rank = "F"
        self.quests = {}
        self.questcount = 0
        self.title = None
    
    def check_rank(self, rank):
        return self.rank == rank
    
    def updaterank(self):
        #check if requirements fulfilled: TODO
        pass 

class Gear():
    def __init__(self, name : str, lore : str, type_ : str, hp : int = 0, atk : int = 0, defense : int = 0, agility : int = 0, phys_atk : int = 0, phys_def : int = 0, mag_atk : int = 0, mag_def : int = 0):
        self.name = name
        self.lore = lore
        self.type_ = type_
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.agility = agility
        self.phyatk = phys_atk
        self.phydef = phys_def
        self.magatk = mag_atk
        self.magdef = mag_def
        
class Item():
    def __init__(self, name, lore):
        self.name = name
        self.lore = lore

class Consumable():
    def __init__(self, name, lore, atk, defense, agility, phys_atk, phys_def, mag_atk, mag_def):
        self.name = name
        self.lore = lore
        self.atk = atk
        self.defense = defense
        self.agility = agility
        self.physatk = phys_atk
        self.physdef = phys_def
        self.magatk = mag_atk
        self.magdef = mag_def

class Error(Exception):
    """Base class for other exceptions"""
    pass

class EndProcess(Erorr):
    """For the three battling functions"""
    pass

from FileMonster import *

fm = FileMonster()
data = fm.load("data")
banned = data.chooseobj("banned") # dictionary of banned playerids
races = data.chooseobj("races")
admin = data.chooseobj("admins") # list of admin ids
players = data.chooseobj("players")
tinteraction = data.chooseobj("tinteraction") # dict {'coords' : {'npc or locations' : {discord.Embed, 'paths'}}
playerlist = list(players)
map_ = data.chooseobj("map") # nested list
baninfo = data.chooseobj("baninfo") #dict {'playerid' : [banreason, date of ban, banned by who]}
places = data.chooseobj("places")
skills = data.chooseobj("skills")
levels = data.chooseobj("levels")
locationinfo = data.chooseobj("locationinfo") # dict {'coords' : discord.Embed}
mobs = data.chooseobj("mobs") #{1 : {mob : [minlevel, maxlevel, multiplier, phys_atk, mag_atk, phys_def, mag_def, cooldown]}}
guilds = data.chooseobj("guilds") # dict {'guildname' : guild instance}
gear = data.chooseobj("gear")

#setup begin
with open('token', 'rb') as readfile:
    TOKEN = pickle.load(readfile)

intents = discord.Intents.all()

##client = discord.Client(activity = discord.Game(name=",help"))
client = commands.Bot(command_prefix = ",", activity = discord.Game(name=",help"), intents=intents, help_command = None)


guildmaster = Role('Guild Master', 0, kickPerms = True, invitePerms = True, setrolePerms = True, rolecreationPerms = True, editPerms = True)
member = Role('Member', 6)

        

async def checkstart(ctx, game = False, private = False) -> bool: #could make it into a decorator
    """
    to check if bot should reply to player's sent command or not
    if return value is false, bot doesn't reply to player else bot carries out function
    """
    channel = ctx.channel.type
    channel = str(channel)
    name = ctx.author.name
    if str(ctx.author.id) in banned:
        await ctx.send("Sorry! You are banned.")
        return False
    
    elif channel == "private" and not private:
        return False
    
    if not game:
        return True
    elif str(ctx.author.id) not in players:
        await ctx.send("You haven't started your adventure yet! Start it with `,start`")
        return False
    
    elif players[str(ctx.author.id)].fightstat[0]:
        await ctx.send("You are currently in a fight! Focus on it!")
        return False
    
    else:
        return True

backgroundtime = 0

@client.event
async def on_ready():
    servers = 0
    print("Connected servers:")
    for guild in client.guilds:
        print(guild.name, guild.id)
        servers+=1
    print(f"\n\n{client.user} has connected to Discord on {servers} servers.")
    async def timer():
        global backgroundtime
        while True:
            backgroundtime += 1
            await asyncio.sleep(1)
    await asyncio.ensure_future(timer())

invite_link = "https://discord.com/api/oauth2/authorize?client_id=744156360094253107&permissions=8&scope=bot"

prefix = ","

#Setup finished
#functions begin


@client.command(aliases = ["inv"])
async def invite(ctx):
    check = await checkstart(ctx)
    if not check:
        return
    embedVar = discord.Embed(title = "Invite the bot and play with your friends!", description = invite_link)
    await ctx.send(embed=embedVar)

@client.command()
async def server(ctx):
    check = await checkstart(ctx)
    if not check:
        return
    await ctx.trigger_typing()
    yeet = ctx.guild
    embedVar = discord.Embed(title = f"{ctx.guild.name}", type = "rich")
    embedVar.add_field(name = "Created", value = yeet.created_at.strftime("%d %B %Y"), inline=True)
    embedVar.add_field(name = "Owner", value = yeet.owner.name, inline = False)
    embedVar.add_field(name = "Total Members", value = yeet.member_count, inline=False)
    embedVar.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
    embedVar.set_thumbnail(url = yeet.icon_url)
    await ctx.send(embed=embedVar)

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency, 2)}ms")

@client.command()
async def help(ctx):
    check = await checkstart(ctx)
    if not check:
        return
    await ctx.trigger_typing()
    embedVar = discord.Embed(title = "General Commands List")
    embedVar.add_field(name = ",help", value = "Shows this lol", inline=False)
    embedVar.add_field(name = ",invite", value = "Gets the invite link of the bot", inline=False)
    embedVar.add_field(name = ",server", value = "Gets information on the server", inline = False)
    embedVar.add_field(name = ",purge (messages)", value = "Purges an amount of messages given that you have the correct permissions", inline = False)
    embedVar.add_field(name = ",gamehelp", value = "Shows the help menu for game commands", inline=False)
    await ctx.send(embed = embedVar)

    
@client.command(aliases = ["clear"])
async def purge(ctx, amount = 0):
    check = await checkstart(ctx)
    if not check:
        return
    perms = ctx.author.guild_permissions.manage_messages
    botperms = ctx.guild.me.guild_permissions.manage_messages
    if not perms:
        await ctx.send("You need the manage messages permission!")
        return
    elif not botperms:
        await ctx.send("I need the manage messages permission!")
        return
    elif amount <= 0:
        await ctx.send("Invalid number!\n`,purge (amount of messages)`")
        return
    await ctx.channel.purge(limit=amount+1)

@client.command(aliases = ["ghelp"])
async def gamehelp(ctx):
    check = await checkstart(ctx)
    if not check:
        return
    embed = discord.Embed(title = "Game Commands", colour = discord.Color.blue())
    embed.add_field(name = ",ghelp", value = "shows this lol")
    embed.add_field(name = ",start", value = "starts your adventure", inline= False)
    embed.add_field(name = ",player", value = "shows your player info", inline= False)
    embed.add_field(name = ",stats", value = "shows your stats", inline = False)
    embed.add_field(name = ",guildhelp", value = "shows all the commands in relation to guilds", inline = False)
    embed.add_field(name = ",move (direction)", value = "moves you in the map. directions - up, right, left, down", inline =False)
    embed.add_field(name = ",map", value = "displays the map", inline = False)
    embed.add_field(name = ",pcreate", value = "creates a party", inline = False)
    embed.add_field(name = ",pleave", value = "leaves your party", inline = False)
    embed.add_field(name = ",pdisband", value = "disbands your party", inline = False)
    embed.add_field(name = ",pinvite @user", value = "invites someone to your party", inline=False)
    embed.add_field(name = ",tinfo", value = "shows the info of the town you are currently in", inline = False)
    embed.add_field(name = ",tinteract (interactable)", value = "interacts with specified npc or location", inline=False)
    embed.add_field(name = ",gear", value = "shows your gear", inline=False)
    embed.add_field(name = ",showinv", value = "shows your inventory", inline = False)
    await ctx.send(embed = embed)

@client.command()
async def start(ctx):
    """
    Commmand used to start playing the game
    """
    check = await checkstart(ctx, private = True)
    if not check:
        return
    def checknum(message):
        return message.author == ctx.author
    if str(ctx.author.id) in players:
        await ctx.send("You already have a save! Are you sure you want to create a new save? [y/n]")
        playerins = players[f'{ctx.author.id}']
        try:
            _ = await client.wait_for("message", check=checknum, timeout = 20)
            _ = _.content
            if _.lower() != "y":
                await ctx.send("Cancelled.")
                return
            elif playerins.guild != None:
                await ctx.send("You're still in a guild! Disband it or transfer ownership to someone first!")
                return
            elif playerins.party != None:
                await ctx.send("You're still in a party! Disband it or transfer ownership to someone first!")
                return
            
        except asyncio.TimeoutError as e:
            await ctx.send("You took too long")
            return

            
    await ctx.send("You can do this tutorial in DMs, it might be better, continue? (enter 'yes' or 'no' in chat)")
    try:
        _ = await client.wait_for("message", check= checknum, timeout = 15)
        _ = _.content
        if _.lower() != "yes":
            await ctx.send("Tutorial cancelled. Type `,start` in my DMs if you wish to conduct the tutorial in DMs.")
            return

    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return
    
    embed = discord.Embed()
    embed.insert_field_at(index = 2, name = "__**Random Bear**__", value = "Hey! I'm Elston, I somehow turned into a bear. Anyways, I see that you want to start your adventure! First things first, you need to pick a race! Here are the list of races to choose from!", inline= False)
    embed.set_thumbnail(url = "https://m.media-amazon.com/images/I/51Q30qp+LEL._AC_SX355_.jpg")
    await ctx.send(embed= embed)
    embed = discord.Embed()
    embed.add_field(name = "1 - Royal-Blooded", value = "10% looting, 17% hp, 5% mag atk\n*The descendants of the late Camelton King The II, the royal blood in them sharply increases their health points.*")
    embed.add_field(name = "2 - Elf", value = "10% agility, 15% mag atk, 15% mag def, -50% phys atk, -10% phys def\n*The Elves, empowered by years of constant magic training and ancient practices, possess high magic powers.*")
    embed.add_field(name = "\u200b", value = "\u200b", inline = False)
    embed.add_field(name = "3 - Cat Person", value = "22% agility, 15% cooldown speed, 5% defense\n*Cat People, with their cat-like abilities, are the fastest amongst all the races. With lower cooldowns and higher agility to increase crit chance, they are a force to be reckoned with.*")
    embed.add_field(name = "4 - Human", value = "20% looting, 5% hp, 5% agility\n*Human.*")
    embed.add_field(name = "\u200b", value = "\u200b", inline = False)
    embed.add_field(name = "5 - Demon", value = "20% phys atk, 15% phys def, -60% mag atk, - 10% mag def\n*The Demons only know destruction and chaos, with remarkably high physical stats, they have extremely low magic stats.*")
    await ctx.send(embed = embed)
    embed = discord.Embed()
    embed.add_field(name = "__**Elston**__", value = "Now enter the number beside the race you want to pick to choose it!")
    embed.set_thumbnail(url = "https://m.media-amazon.com/images/I/51Q30qp+LEL._AC_SX355_.jpg")
    await ctx.send(embed = embed)
        
    try:
        number = await client.wait_for("message", check=checknum, timeout = 45)
        number = number.content
        if number not in ['1', '2', '3', '4', '5']:
            await ctx.send("Invalid number! Enter the number beside the races next time!")
            return
        else:
            embed = discord.Embed()
            embed.add_field(name = "__**Elston**__", value = "Good choice! Now what is your name adventurer? (alphanumeric only and must be more than 2 characters)")
            embed.set_thumbnail(url = "https://m.media-amazon.com/images/I/51Q30qp+LEL._AC_SX355_.jpg")
    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return
        
    await ctx.send(embed = embed)
    number = int(number)
    racelist = list(races)
    playerrace = racelist[number-1]
    try:
        playername = await client.wait_for("message", check=checknum, timeout = 20)
    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return
    playername = playername.content
    if not playername.isalnum():
        await ctx.send("Player name has to be alphanumerical. Try again next time!")
        return
    elif len(playername) < 3:
        await ctx.send("Length of name has to be more than 2. Try again next time!")
        return
    elif playername in players:
        await ctx.send("Name taken! Try again next time!")
        return
    playerins = Player(playername, playerrace)
    players[f'{ctx.author.id}'] = playerins
    await ctx.send("Player registered.")
    embed = discord.Embed()
    embed.add_field(name = "__**Elston**__", value = f"Welcome to Sword Tale {playername}! Your only current skill is 'punch', use it enough and who knows what will happen? You can explore the world of Anomopheric to\
 kill monsters to gain loot and exp to get more powerful, complete dungeons/raids to get dungeon/raid loot, discover new things, items, mechanics, skills. Large interactive map and exploration available to you in Sword Tale!")
    embed.set_thumbnail(url = "https://m.media-amazon.com/images/I/51Q30qp+LEL._AC_SX355_.jpg")
    await ctx.send(embed = embed)
    embed = discord.Embed(title = "Be the first person or guild to raid and complete dungeons! There are much to be discovered and much that are hidden. Hopefully you find them all ;)")
    embed.add_field(name = "\u200b", value = "-From yours truly, Elston")
    await ctx.send(embed = embed)
    racestat = races[playerrace]
    for stat in racestat:
        playerins.statsp[stat] += racestat[stat]

    
#internal functions
async def rewards(playerins, mobins):
    '''
    A function to give players rewards(exp, gold, items)
    when they win a battle
    '''
    expgain = round(3.5*mobins.level)
    goldgain = round(4.2*mobins.level)
    

async def addstuff(playerins, stuff : list):
    for i in stuff:
        playerins.inventory[i] += 1

async def randmob(playerins):
    """
    generate a random mob based on location
    """
    coords = playerins.location[0]
    coords = coords.split('-')
    coord1 = int(coords[0])
    coord2 = int(coords[1])
    if coord2 in range(0, 7) and coord1 in range(3, 6):
        mob = mobs[1]

    mobchoice = random.choice(list(mob))
    mobins = mob[mobchoice]
    moblevel = random.randint(mobins[0], mobins[1])
    multiplier = mobins[2]
    atk = round(3.4*moblevel*multiplier)
    hp = round(15*moblevel*multiplier)
    defense = round(1.2*moblevel*multiplier)
    phys_atk = round(mobins[3]*moblevel)
    phys_def = round(mobins[4]*moblevel)
    mag_atk = round(mobins[5]*moblevel)
    mag_def = round(mobins[6]*moblevel)
    cooldown = mobins[7]
    mob = Mob(mobchoice, moblevel, atk, hp, defense, phys_atk, phys_def, mag_atk, mag_def, cooldown, multiplier)
    return mob
    
async def monsterattack(ctx, playerins, mob):
    """
    calculates mob damage done and subtracts that from player's hp
    sends an embed object back to show how much health each of them has left
    """
    dmg = await calcmobdmg(playerins, mob)
    playerins.stats['hp'] -= dmg
    embed = discord.Embed(title =f"**__{playerins.user}'s Battle Status__**", description = f"Lvl {mob.level} {mob.name} has attacked you for {dmg} damage!")
    embed.add_field(name = f"**__Level {mob.level} {mob.name}__**", value = "\u200b", inline=False)
    embed.add_field(name=f"**Health :heart: {mob.hp}**", value = "\u200b", inline=False)
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = f"**__{playerins.user}__**", value = "\u200b", inline=False)
    embed.add_field(name = f"**Health :heart: {playerins.stats['hp']}**", value = "\u200b", inline=False)
    await ctx.send(embed=embed)
    
    
#async def battle(ctx, mob, dmg, seconds):
#    playerins = players[f'{ctx.author.id}']
#    
#    def check(message):
#        return message.author == ctx.author
#    mobattack = returntaskmobattack(seconds, monsterattack, ctx, playerins, dmg, mob)
#    mobattack = await mobattack
#    while True:
#        await client.wait_for("message", check = check, timeout = 121)

async def taskbattle(ctx, playerins, mob):
    """
    runs the monsterattack function which the mob damages the player and passes control for x seconds
    where x is the number put in the seconds parameter which also represents the monster's attack cooldown
    if player's hp is more than 0 otherwise checks if player has a party or not, if no, return 0
    otherwise, check if all party members are dead if not, remove current player from alive list in main battle function
    """
    seconds = mob.cooldown
    if playerins.party:
        alive = [players[i] for i in playerins.party.members] #makes a list of player instances from party members

    while True:
        _ = await monsterattack(ctx, playerins, mob)
        if not playerins.stats['hp'] < 1:
            await asyncio.sleep(seconds)
        elif not playerins.party:
            return 0
        else:
            playerins.fightstat[1] = 0
            members = playerins.party.members
            check = False
            for i in members:
                member = players[i]
                if member.fightstat[1]:
                    check = True
                    
            if not check:
                return 0
            else:
                index = alive.index(playerins)
                del alive[index]
                playerins = random.choice(alive)


async def returntaskmobattack(ctx, playerins, mob):
    """
    basically just returns taskbattle as a task using version 3.6.3 asyncio so that it can be used to run later along with other tasks
    """
    tasktest = asyncio.ensure_future(taskbattle(ctx, playerins, mob))
    return tasktest
          
async def effectdmgplayer(ctx, dmg, seconds, playerins):
    pass
                    
async def effectdmgmob(ctx, dmg, seconds, mobins):
    pass
            

async def gearvalues(playerins) -> dict:
    '''
    calculates and returns a dictionary stating
    the total magic defense, physical attack, magic attack, physical defense
    values of the player's current equipped gear
    '''
    playergear = playerins.gear
    totalphyatk = totalmagdef = totalphydef = totalmagatk = 0
    
    for i in playergear:
        gear = playergear[i]
        if not gear:
            continue
        totalphyatk += gear.phyatk
        totalmagdef += gear.magdef
        totalmagatk += gear.magatk
        totalphydef += gear.phydef
    
    return {'phyatk' : totalphyatk,
            'phydef' : totalphydef,
            'magatk' : totalmagatk,
            'magdef' : totalmagdef}


async def calcplayerdmg(playerins , mobins, skillphyatk, skillmagatk):
    '''
    calculates teh true damage a player does
    '''
    def default(value : float) -> int:
        if value <= 0:
            return 1
        else:
            return round(value)
    playerstats = playerins.stats
    gearvalue = await gearvalues(playerins)
    playerphyatk = gearvalue['phyatk']
    playermagatk = gearvalue['magatk']
    playerOriginalDmg = (playerstats['atk'] * playerphyatk) + default(playerphyatk * skillphyatk * playerstats['phys_atk'] - mobins.phys_def * mobins.level) + default(playermagatk * skillmagatk * playerstats['mag_atk']- mobins.mag_def*mobins.level)
    playerTrueDmg = default(playerOriginalDmg - mobins.defense)   
    return playerTrueDmg

async def calcmobdmg(playerins, mobins):
    '''
    calculates the true damage a mob does
    '''
    def default(value : float) -> int:
        if value <= 0:
            return 1
        else:
            return round(value)
    gearvalue = await gearvalues(playerins)
    gearphydef = gearvalue['phydef']
    gearmagdef = gearvalue['magdef']
    playerstats = playerins.stats
    mobOriginalDmg = mobins.atk + default(mobins.phys_atk - playerstats['phys_def'] * gearphydef) + default(mobins.mag_atk - playerstats['mag_def'] * gearmagdef)
    mobTrueDmg = mobOriginalDmg - playerstats['defense']
    return default(mobTrueDmg)
        
            
async def messageattack(ctx, check ,buffs, mobins): #if partymembers != None, Party instance
    """
    waits for player to send a message and check if its a valid move then does some calculation and subtracts that
    from monster's health and displays in an embed object the skill used and health of both entities or if 
    player is in a party, mob and all players' hp then add the buffs given by the used skill to the player
    """
    playerins = players[str(ctx.author.id)]
    partymembers = playerins.party
    while True:
        try:
            _ = await client.wait_for("message", check = check, timeout = 540)

        except asyncio.TimeoutError as e:
            await ctx.send("You took too long thus the battle has ended you slowpoke.")
            return 0
            if not partymembers:
                playerins.stats['hp'] = 0
            else:
                for i in partymembers.members:
                    playerins = players[i]
                    playerins.stats['hp'] = 0
            return 0
        playerins = players[str(_.author.id)]
        _ = _.content
        #ctx might not be referring to the sender of the message
        try:
            skillinfo = playerins.skills[_]
            skillname = skillinfo[3]
            mag_atk = skillinfo[5]
            phys_atk = skillinfo[4]
            skillbuff = skillinfo[6]
            dmg = await calcplayerdmg(playerins, mobins, phys_atk, mag_atk)
            mobins.hp -= dmg
            for i in skillbuff: #i = buff name
                if i in list[buffs]: #buffs dont stack
                    continue
                addbuff = []
                for j in skillbuff[i][1]:
                    originalstat = playerins.stats[j]
                    playerins.stats[j] *= skillbuff[i][1][j] #multiplies player's current specific stats with the multiplier 
                    difference = playerins.stats[j] - originalstat #states the diffrence in numerical value
                    addbuff.append(f'{j}:{difference}')
                
                buffs[i] = [' '.join(addbuff)] + [backgroundtime, skillbuff[i][0]]
                
                    
            embed = discord.Embed(title =f"**{playerins.user}'s __Battle Status__**", description = f"You used {skillname} to deal {dmg} damage to the monster!")
            embed.add_field(name = f"**__{mob.name}__**", value = "\u200b", inline=False)
            embed.add_field(name=f"**Health :heart: {mob.hp}**", value = "\u200b", inline=False)
            embed.add_field(name = "\u200b", value = "\u200b", inline=False)
            embed.add_field(name = f"**__{playerins.user}__**", value = "\u200b", inline=False)
            embed.add_field(name = f"**Health :heart: {playerins.stats['hp']}**", value = "\u200b", inline=False)
                
        except:
            await ctx.send("Skill not found!")

        await asyncio.sleep(1)

async def secondcheck(ctx, mobattack, checkmessage, mob, playerins, buffs : dict):
# buffs {"buffname" : ["effects"('statname:value(buff values would be in percentages but here itll be the numerical value of the percentageinc/dec)statname2:value'), backgroundtime at which it had been applied, duration]}
    """
    checks every second in the background while battle is going on to see if player or mob has died and if so, cancels everything
    to end the battle, checks also for buffs wether they have ended or not
    """
    if not playerins.party:
        checkdead = "playerins.stats['hp'] <= 0"
    else:
        partyins = playerins.party
        checkdead = "partyins.checkdead()" #false = not all dead
    while True:
        if any([
            mob.hp <= 0,
            eval(checkdead),
            messageattack.done()
            ]):
            monsterattack.cancel()
            messageattack.cancel()
            mobattack.cancel()
            break
        for i in buffs:
            buff = buffs[i] #list
            time = backgroundtime
            time -= buff[1] #time(seconds) passed after buff had been applied
            if time >= buff[2]:
                effects = buff[0]
                effects = effects.split()
                for j in effects:
                    j = j.split(':')
                    buffname = j[0]
                    buffvalue = j[1]
                    exec(f'playerins.stats[{buffname}] -= {buffvalue}')
                del buffs[i]
        await asyncio.sleep(1)

@client.command()
async def test(ctx):
    def check(message):
        return message.author == ctx.author
    playerins = players[f'{ctx.author.id}']
    mobins = Mob("High Level Demon", 20, 7, 6, 8, 4, 2, 3, 2, 7)
    mobattack = returntaskmobattack(4, monsterattack, ctx, playerins, 5, mobins)
    mobattack = await mobattack
    checkmessage = asyncio.ensure_future(message(ctx, check))
    buffs = {}
    await checkdead(ctx, mobattack, checkmessage, mobins, playerins)
    if playerins.stats['hp'] <= 0:
        await ctx.send("Haha u lost noob idiot")
    else:
        await ctx.send("u won the battle!")
    
#    while not mobattack.done():
#        
#        _ = await client.wait_for("message", check = check, timeout= 130)
#        if _.content == "ow":
#            await ctx.send("haha rekt")


async def singlebattle(ctx, check):
    '''
    Function for letting players battle with monsters. Only works with one person.
    Anyone in a party is not allowed to battle
    '''
    playerins = players[f'{ctx.author.id}']
    mobins = await randmob(playerins)
    mobdamaging = await returntaskmobattack(ctx, playerins, mobins)
    mobdamaging = await mobdamaging
    buffs = {}
    checkmessage = await asyncio.ensure_future(messageattack(ctx, check, buffs, mobins))
    checksecond = await asyncio.ensure_future(secondcheck(ctx, mobdamaging, checkmessage, mobins, playerins, buffs))
    if playerins.stats['hp'] <= 0:
        await ctx.send("Haha u lost noob idiot")
    else:
        await ctx.send("u won the battle!")
    
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is not ready to use, try again in %.2f seconds' % error.retry_after, delete_after=error.retry_after)
        await asyncio(error.retry_after)
        return
    else:
        print(error)

#async def battle(playerins               

#guild commands

@client.command(aliases = ["gcreate"])
async def create_guild(ctx, *, guildname):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    if playerins.guild != None:
        await ctx.send("Error! You are already in a guild!")
        return
    elif len(guildname.split()) > 3 or len(guildname) > 21:
        await ctx.send("Guild name too long!")
        return
    elif guildname in guilds:
        await ctx.send("The guild name already exists!")
        return
    elif playerins.gold < 4000:
        await ctx.send("Not enough gold!")
        return
    
    playerins.gold -= 4000
    guildins = Guild(guildname, f'{ctx.author.id}')
    playerins.guildpos = "Guild Master"
    playerins.guild = guildname
    playerins.guildins = guildins
    await ctx.send(f"Guild '{guildname}' has been created by {ctx.author.name}!")
    guilds[f'{guildname}'] = guildins
    guildins.members[f'{ctx.author.id}'] = f'{playerins.user}'

@client.command(aliases = ["gsetrole", "gset"])
async def guildsetrole(ctx, member : discord.Member, *,  role):
    """
    allows user to edit a specific guild-role's permissions
    """
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f"{ctx.author.id}"]

    try:
        playerins2 = players[f"{member.id}"]
    except:
        await ctx.send("Player hasn't started his/her adventure yet! Start your adventure with `,start`!")
        return
    guild = playerins.guildins
    if playerins2.guild != playerins.guild:
        await ctx.send("Player must be part of your guild!")
        return

    elif not role in guild.rolepos:
        await ctx.send("Role not found!")
        return
    
    elif not guild.roles[f'{playerins.guildpos}'].setrolePerms:
        await ctx.send("You don't have the permissions to do this!")
        return
    role1 = guild.rolepos.index(playerins.guildpos)
    role2 = guild.rolepos.index(playerins2.guildpos)
    oldrole = playerins2.guildpos
    
    try:
        role3 = guild.rolepos.index(role)
    except:
        await ctx.send("The role does not exist! (input is case sensitive)")
        return
    
    if role2 <= role1:
        await ctx.send("User's role is higher or equal to yours.")
        return
    elif role3 == role2:
        await ctx.send("User is already that role")
    elif role1 == role3 or role3 < role1:
        await ctx.send("You do not have permissions to do this!")
        return

    playerins2.guildpos = role
    await ctx.send(f"{playerins2.user}'s role has been set from {oldrole} to {role}!")

@client.command()
async def guildhelp(ctx):
    embed = discord.Embed(title = "Guild Help", colour = discord.Color.green())
    embed.add_field(name = ",guildhelp", value = "shows this lol", inline=False)
    embed.add_field(name = ",create_guild (guild name)", value = "creates a guild (requires 4k gold)")
    embed.add_field(name= ",guild", value = "shows your guild info", inline=False)
    embed.add_field(name = ",ginvite @user", value = "invites someone to your guild")
    embed.add_field(name = ",gleave", value = "leaves the guild you are in", inline = False)
    embed.add_field(name=",gdisband", value = "disbands the guild(must be guild master)")
    embed.add_field(name = ",gset @user (role)", value = "sets guild member's rank to the role specified (must have permissions)(case sensitive)", inline=False)
    embed.add_field(name = ",gcreaterole (role)", value = "creates a new guild role (must have permissions)", inline=False)
    embed.add_field(name = ",geditrole (role)", value = "edits a role's permissions", inline=False)
    embed.add_field(name = ",gmembers", value = "displays all members of the guild you are in ", inline = False)
    await ctx.send(embed=embed)

@client.command(aliases = ["guildinfo"])
async def guild(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    if playerins.guild == None:
        await ctx.send("You're not in a guild!")
        return
    guild = playerins.guildins
    embed = discord.Embed(title = f"**__{playerins.guild}__**")
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    owner = players[guild.owner].user
    embed.add_field(name = "Guild Master :crown:", value = f"{owner}")
    embed.add_field(name = "Value :moneybag:", value = f"{guild.value}")
    _ = 0
    for i in guild.members:
        _ += 1
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "Member Count :page_with_curl:   ", value = f"{_}")
    _ = []
    for i in guild.rolepos:
        if i != 0:
            _.append(i)
    _ = '\n'.join(_)
    embed.add_field(name = "Roles :military_helmet:", value = f"{_}", inline=True)
    await ctx.send(embed = embed)

@client.command(aliases = ["ginv"])
async def ginvite(ctx, member : discord.Member):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    try:
        playerins2 = players[f'{member.id}']
    except:
        await ctx.send("User has not started his/her adventure yet! Start it with `,start`")
        return
    guild = playerins.guildins
    if guild == None:
        await ctx.send(f"You are not in a guild {ctx.author.mention}!")
        return
    elif not guild.roles[f'{playerins.guildpos}'].invitePerms:
        await ctx.send("You do not have permissions to do this!")
        return

    elif playerins2.guild != None:
        await ctx.send("User is already in a guild!")
        return
    def checknum(message):
        return message.author == member  
    await ctx.send(f"{member.mention} you have been invited to join {playerins.guild}. Would you like to join? [y/n]")
    try:
        _ = await client.wait_for("message", check=checknum, timeout = 15)
        _ = _.content
        if _.lower() != "y":
            await ctx.send("Invitation denied.")
            return
        
    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return

    playerins2.guild = playerins.guild
    playerins2.guildins = guild
    playerins2.guildpos = "Member"
    guild.members[f'{member.id}'] = f'{playerins2}'
    guild.value += playerins2.gold
    await ctx.send(f"You have joined {playerins.guild}!")

@client.command(aliases = ["gdelrole", "gdel"])
async def gdeleterole(ctx, *, role):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    guildins = playerins.guildins
    if guildins == None:
        await ctx.send("You aren't even in a guild!")
        return
    elif not guildins.roles[f'{playerins.guildpos}'].rolecreationPerms:
        await ctx.send("Not enough permissions")
        return

    try:
        roleins = guildins.roles[role]
        pos = guildins.rolepos.index(role)
        pos2 = guildins.rolepos.index(playerins.guildpos)
        
    except Exception as e:
        print(e)
        await ctx.send("Role not found!")
        return
    
    if pos2 >= pos:
        await ctx.send("Cannot delete a role higher or equal to your role!")
        return

    guildins.rolepos[pos] = 0
    del guildins.roles[role]
    await ctx.send("Role deleted!")
    
@client.command()
async def gmembers(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    if playerins.guild == None:
        await ctx.send("You are not in a guild!")
        return
    
    guildins = playerins.guildins
    embed = discord.Embed(title = f"**__{guildins.name}'s Members__**")
    for i in guildins.members:
        playeri = players[i]
        embed.add_field(name = f"{playeri.user} - {playeri.guildpos}", value = "\u200b", inline=False)

    await ctx.send(embed=embed)

    
@client.command()
async def gleave(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    if playerins.guild == None:
        await ctx.send("You are not in a guild!")
        return
    elif playerins.guildpos == "Guild Master":
        await ctx.send("You are the guild master, you cannot leave this guild! You can disband the guild using `,gdisband`")
        return
    def check(message):
        return message.author == ctx.author
    guildname = playerins.guild
    await ctx.send(f"Are you sure you want to leave {guildname}? [y/n]")
    try:
        _ = await client.wait_for("message", check = check, timeout = 15)
        _ = _.content

    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return
    if _.lower() != "y":
        await ctx.send("Cancelled.")
        return
    playerins.guild = None
    playerins.guildins.value -= playerins.gold
    del playerins.guildins.members[f'{ctx.author.id}']
    playerins.guildins = None
    playerins.guildpos = None
    await ctx.send(f"You have left {guildname}")
    
@client.command()
async def gdisband(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    if playerins.guild == None:
        await ctx.send("You are not in a guild!")
        return
    elif playerins.guildpos != "Guild Master":
        await ctx.send("You do not have the permissions to do this!")
        return
    
    def check(message):
        return message.author == ctx.author
    await ctx.send("Are you sure you want to disband the guild? [y/n]")
    try:
        _ = await client.wait_for("message", check = check, timeout = 15)
        _ = _.content
        if _.lower() != "y":
            await ctx.send("Cancelled.")
            return

    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return
    
    guild = playerins.guildins
    for i in guild.members:
        playerins = players[i]
        playerins.guild = None
        playerins.guildpos = None
        playerins.guildins = None
        
        
    await ctx.send("Guild has been disbanded!")

@client.command()
async def gcreaterole(ctx, *, name):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    guildins = playerins.guildins
    if playerins.guild == None:
        await ctx.send("You are not in a guild!")
        return
    elif not guildins.roles[f'{playerins.guildpos}'].rolecreationPerms:
        await ctx.send("You do not have enough permissions!")
        return

    elif not 0 in guildins.rolepos:
        await ctx.send("The guild has reached the maximum limit of having 5 custom roles!")
        return

    elif len(name.split()) > 3 or len(name) > 15:
        await ctx.send("Role name is too long!")
        return
    
    rolepos = guildins.rolepos
    position = rolepos.index(f'{playerins.guildpos}')
    if not 0 in rolepos[position:]:
        await ctx.send("You cannot create a role that is higher position than you!")
        return
    pos = []
    count = 0
    for i in rolepos[position+1:]:
        count+=1
        if i == 0:
            pos.append(str(position+count))
    await ctx.send(f"The available positions for the role are `{' '.join(pos)}` the lower number the higher the rank")
    await ctx.send(f"What position would you like {name} to be in?")
    def check(message):
        return message.author == ctx.author
    try:
        _ = await client.wait_for("message", check = check, timeout = 20)
        _ = _.content
        if not _.isdigit():
            await ctx.send("Invalid input")
            return
        elif _ not in pos:
            await ctx.send("Please enter a valid position next time!")
            return

    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return
        
    roleins = Role(name, int(_))
    guildins.rolepos[int(_)] = name
    guildins.roles[f'{name}'] = roleins
    await ctx.send(f"Role {name} created!")
    

@client.command()
async def geditrole(ctx, *, rolename):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    guildins = playerins.guildins
    if guildins == None:
        await ctx.send("You aren't even in a guild!")
        return
    elif not guildins.roles[f'{playerins.guildpos}'].editPerms:
        await ctx.send("Not enough permissions")
        return

    try:
        roleins = guildins.roles[rolename]
        pos = guildins.rolepos.index(rolename)
        pos2 = guildins.rolepos.index(playerins.guildpos)
        
    except Exception as e:
        print(e)
        await ctx.send("Role not found!")
        return
    
    if pos2 >= pos:
        await ctx.send("Cannot edit a role higher or equal to your role!")
        return
    def check(message):
        return message.author == ctx.author
    _ = ""
    while True:
        embed = discord.Embed(title = f"{roleins.name} Permissions", description = "Type in the permissions name to switch it's value, case sensitive (type 'cancel' to cancel)")
        embed.add_field(name = "kick", value = f"**{roleins.kickPerms}** - Permission to kick members of the guild", inline = False)
        embed.add_field(name = "invite", value = f"**{roleins.invitePerms}** - Permission to invite members into the guild", inline = False)
        embed.add_field(name = "setrole", value = f"**{roleins.setrolePerms}** - Permission to change the roles of guild members")
        embed.add_field(name = "rolecreation", value = f"**{roleins.rolecreationPerms}** - Permission to create roles for the guild", inline=False)
        embed.add_field(name = "edit", value = f"**{roleins.editPerms}** - Permission to edit role permissions")
        embed.add_field(name = "name (new name)", value = "Changes the name of this role", inline=False)
        await ctx.send(embed=embed)
        try:
            _ = await client.wait_for("message", check=check, timeout=25)
            _ = _.content
            splitted = _.split()
            if _.lower() == "cancel":
                await ctx.send("Cancelled.")
                return
            elif splitted[0] == "name":
                newname = ' '.join(splitted[1:])
                print(newname)
                del guildins.roles[roleins.name]
                roleins.name = newname
                print(roleins.name)
                guildins.roles[newname] = roleins
                guildins.rolepos[pos] = newname
            
            elif eval(f"roleins.{_}Perms"):
                exec(f"roleins.{_}Perms = False")
            else:
                exec(f"roleins.{_}Perms = True")
            
            

        except asyncio.TimeoutError as e:
            await ctx.send("You took too long!")
            return

        except Exception as e:
            print(e)
            await ctx.send("Invalid input!")
            return

                   
                   
                   
                   
                   
    
        
#game commands

@client.command()
async def gear(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return

    playerins = players[f'{ctx.author.id}']
    embed = discord.Embed(title = f"{playerins.user}'s Gear :mechanical_arm:")
    gear = playerins.gear
    _ = list(gear)
    for i in _:
        embed.add_field(name = f"{i}", value = f"{gear[i]}", inline=False)
    await ctx.send(embed = embed)

@client.command()
async def showinv(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    inv = playerins.inventory
    embed = discord.Embed(title = f"{playerins.user}'s Inventory :school_satchel:")
    for count, item in enumerate(inv):
        embed.add_field(name = f"Slot {count}", value = f"{item.name}  x{inv[item]}", inline=False)
    await ctx.send(embed=embed)
    

@client.command(aliases = ["ag"])
async def advguild(ctx):
    check = await checkstart(ctx, game =True)
    if not check:
        return
    playerins = players[str(ctx.author.id)]
    embed = discord.Embed(title = "**__Guild Master Yuki greets you with a gentle smile and asks what you would like to do today__**")
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "**Options**", value = "\u200b")
    embed.add_field(name = "*1) Get your adventurer card*", value = "\u200b", inline=False)
    embed.add_field(name = "*2) Upgrade your adventurer rank*", value = "\u200b", inline=False)
    embed.add_field(name = "*3) See quests*", value = "\u200b", inline=False)
    embed.add_field(name = "*4) See shop*", value = "\u200b", inline=False)
    embed.add_field(name = "*5) Nevermind lol*", value = "\u200b", inline=False)
    embed.set_footer(text = "Enter the number of your option")
    await ctx.send(embed=embed)
    def check(message):
        return message.author == ctx.author
    txt = await client.wait_for(message, check, 50)
    if txt == "1":
        if playerins.advcard:
            await ctx.send("You already have an adventurer card!")
            return
    elif txt == "2":
        pass
        # MARK:- TODO: What does this do??

@client.command(aliases = ["towninfo"])
async def tinfo(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    location = playerins.location[0]
    try:
        embed = locationinfo[location]
    except:
        embed = discord.Embed(title = "**__The Wilderness__**", description = "Just the wilderness. Where are you going?")
    await ctx.send(embed=embed)

@client.command(aliases = ["tint", "interact"])
async def tinteract(ctx, *, aim):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    coords = playerins.location[0]
    
    def check(message):
        return message.author == ctx.author
    
    try:
        embeddict = tinteraction[coords][aim]
        embedlist = embeddict['first']
        embed = embedlist[0]
    except:
        await ctx.send(f"{aim} not found as an interactable!")
        return
    
    while True:
        await ctx.send(embed = embed)
        if len(embedlist) == 1:
            return
        _ = await client.wait_for("message", check=check, timeout = 120)
        _ = _.content
        if _ not in embedlist:
            await ctx.send("Invalid path!")
            return
        embedlist = embeddict[_]
        embed = embedlist[0]


@client.command(aliases = ["pcreate", "createp"])
async def createparty(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    if not playerins.party == None:
        await ctx.send("You are already in a party!")
        return

    partyins = Party(f"{ctx.author.id}")
    playerins.party = partyins
    await ctx.send("Party created!")

@client.command(aliases = ["partyleave", "leavep"])
async def pleave(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    if playerins.party == None:
        await ctx.send("You are not in a party!")
        return
    partyins = playerins.party
    if partyins.owner == str(ctx.author.id):
        await ctx.send("You're the owner of the party! Disband it or transfer ownership to someone else!")
        return
    playerins.party = None
    await ctx.send("You have left your party!")



@client.command()
async def pdisband(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    partyins = playerins.party
    if partyins == None:
        await ctx.send("You are not in a party!")
        return
    elif partyins.owner != str(f'{ctx.author.id}'):
        await ctx.send("You must be the party leader to disband!")
        return
    for i in partyins.members:
        playeri = players[f'{i}']
        playeri.party = None
    await ctx.send("Party has been disbanded!")


@client.command(aliases = ["pinv"])
async def pinvite(ctx, member : discord.Member):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    playerins2 = players[f'{member.id}']
    partyins = playerins.party
    if partyins == None:
        await ctx.send("You are not in a party!")
        return
    elif partyins.owner != str(f'{ctx.author.id}'):
        await ctx.send("You must be the party leader to invite!")
        return

    elif playerins2.party != None:
        await ctx.send("User is already in a party")
        return

    await ctx.send(f"{member.mention} you've been invited to {playerins.user}'s party! Accept the invite? [y/n]")
    def check(message):
        return message.author == member
    try:
        _ = await client.wait_for("message", check=check, timeout=15)
        _ = _.content
        if _.lower() != "y":
            await ctx.send("Invite declined!")
            return

    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return

    playerins2.party = partyins
    partyins.members.append(str(member.id))
    await ctx.send("You have accepted the invite!")

    
@client.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def move(ctx, direction):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    if direction not in ["right", "left", "up", "down"]:
        await ctx.send("Invalid direction! Valid directions: `right, left, up, down`")
        return
    
    playerins = players[f'{ctx.author.id}']
    coords = playerins.location[0]
    if direction == "up":
        if int(coords[0]) - 1 == -1:
            await ctx.send("A mysterious barrier blocks your path...")
            return
        _ = int(coords[0])-1
        playerins.location[0] = f"{_}-{coords[2]}"

    elif direction == "down":
        if int(coords[0])+1 == 10:
            await ctx.send("A mysterious barrier blocks your path...")
            return
        _ = int(coords[0])+1
        playerins.location[0] = f"{_}-{coords[2]}"

    elif direction == "right":
        if int(coords[2])+1 == 10:
            await ctx.send("A mysterious barrier blocks your path...")
            return
        _ = int(coords[2])+1
        playerins.location[0] = f"{coords[0]}-{_}"

    else:
        if int(coords[2])-1 == -1:
            await ctx.send("A mysterious barrier blocks your path...")
            return
        _ = int(coords[2])-1
        playerins.location[0] = f"{coords[0]}-{_}"

    try:
        playerins.location[1] = places[playerins.location[0]]

    except:
        playerins.location[1] = "Wilderness - Where monsters roam"
    await ctx.send(f"You moved {direction}")
            
@client.command()
async def map(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    embed = discord.Embed(title = "Map :compass:", colour = discord.Colour.orange())
    embed.add_field(name="\u200b", value = "\u200b", inline=False)
    for i in map_:
        embed.add_field(name = "\u200b", value = f'{"".join(i)}', inline=False)
    await ctx.send(embed=embed)

@client.command(aliases = ["stat"])
async def stats(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    player = players[str(ctx.author.id)]
    playerstats = player.statsp
    embed = discord.Embed(title = f"**__{player.user}'s Stats__**\t\t\t**__{player.race}__**")
    embed.add_field(name = "\u200b", value = "\u200b")
    embed.add_field(name = "**__Percentages__**", value = "\u200b")
    embed.add_field(name = "\u200b", value = "\u200b")
    embed.add_field(name = "MaxHP :heart:", value = f"{playerstats['maxhp']}%")
    embed.add_field(name = "Agility :dash:", value = f"{playerstats['agility']}%")
    embed.add_field(name = "Looting :money_mouth:", value = f"{playerstats['looting']}%")
    embed.add_field(name = "Attack :dagger:", value = f"{playerstats['atk']}%")
    embed.add_field(name = "Defense :shield:", value = f"{playerstats['defense']}%")
    embed.add_field(name = "Physical Attack", value = f"{playerstats['phys_atk']}%")
    embed.add_field(name = "Physical Defense", value = f"{playerstats['phys_def']}%")
    embed.add_field(name = "Magic Attack", value = f"{playerstats['mag_atk']}%")
    embed.add_field(name = "Magic Defense", value = f"{playerstats['mag_def']}%")
    embed.add_field(name = "Cooldown Speed", value = f"{playerstats['cooldown_speed']}%")
    embed.add_field(name = "\u200b", value = "\u200b")
    embed.add_field(name = "\u200b", value = "\u200b")
    playerstats = player.stats
    embed.add_field(name = "\u200b", value = "\u200b")
    embed.add_field(name = "**__Actual Value__**", value = "\u200b")
    embed.add_field(name = "\u200b", value = "\u200b")
    embed.add_field(name = "Max HP :heart:", value = f"{playerstats['maxhp']}")
    embed.add_field(name = "HP :heart:", value = f"{playerstats['hp']}")
    embed.add_field(name = "Agility :dash:", value = f"{playerstats['agility']}")
    embed.add_field(name = "Attack :dagger:", value = f"{playerstats['atk']}")
    embed.add_field(name = "Defense :shield:", value = f"{playerstats['defense']}")
    embed.add_field(name = "Physical Attack", value = f"{playerstats['phys_atk']}")
    embed.add_field(name = "Physical Defense", value = f"{playerstats['phys_def']}")
    embed.add_field(name = "Magic Attack", value = f"{playerstats['mag_atk']}")
    embed.add_field(name = "Magic Defense", value = f"{playerstats['mag_def']}")
    embed.add_field(name = "Looting :money_mouth:", value = f"{playerstats['looting']}")
    embed.add_field(name = "Cooldown Speed", value = f"{playerstats['cooldown_speed']}")
    await ctx.send(embed=embed)

@client.command(aliases = ["playerinfo"])
async def player(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerstat = players[f'{ctx.author.id}'] #gets player instance of sender
    embed = discord.Embed(title = f"**__{playerstat.user}'s Info__**          **__Status: {playerstat.status}__**")
    embed.add_field(name = "Gold :coin:", value = f"{playerstat.gold}")
    embed.add_field(name = "Race :flag_white:", value = f"{playerstat.race}", inline = True)
    embed.add_field(name = "Level :arrow_up:", value = f"{playerstat.level} [{playerstat.exp}/{levels[playerstat.level]}]", inline = True)
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "Co-ords :compass:", value = f"{playerstat.location[0]}")
    embed.add_field(name = "Location :map:", value = f"{playerstat.location[1]}")
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "Guild :beginner:", value = f"{playerstat.guild}", inline = True)
    embed.add_field(name = "Guild Position :military_helmet:", value = f"{playerstat.guildpos}", inline=True)
    _ = playerstat.party
    if _ != None:
        _ = "True"
    embed.add_field(name = "Party Status :partying_face:", value = f"{_}")
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    _ = '\n'.join(list(playerstat.skills))
    embed.add_field(name = "Skills :bulb:", value = f"{_}")
    _ = []
    t = []
    for i in playerstat.skills:
        if playerstat.skills[i] == None:
            continue
        _.append(f"{playerstat.skills[i][3]}")
        t.append(f"{playerstat.skills[i][2]}")
    _ = '\n'.join(_)
    t = '\n'.join(t)
    embed.add_field(name = "Keybind :keyboard:", value = f"{_}")
    _ = []
    embed.add_field(name = "Skill Mastery :low_brightness:", value = f"{t}")
    await ctx.send(embed= embed)

@client.command()
async def explore(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    location = playerins.location[0]
    location = location.split('-')
    if map_[int(location[0])][int(location[1])] == 't':
        await ctx.send("You cannot do this in a town!")
        return
    elif playerins.stats['hp'] <= 0:
        await ctx.send("Dude you don't have health.")
        return
    if playerins.party == None:
        partymembers = None
        def check(message):
            return all([message.author == ctx.author, message.content in players[str(ctx.author.id)].skills])
    else:
        partymembers = playerins.party.members
        def check(message):
            return all([message.author in partymembers, message.content in players[str(message.author.id)].skills])
    await singlebattle(ctx, check)
            
    #message(ctx, check, partymembers)
        
##    mobattack = returntaskmobattack(mobins.cooldown, monsterattack, ctx, playerins, mobdmg, mobins)
##    mobattack = await mobattack
##    checkmessage = asyncio.ensure_future(message(ctx, check, partymembers))
##    await checkdead(ctx, mobattack, checkmessage, mobins, playerins)
##    if playerins.stats['hp'] <= 0:
##        await ctx.send("Haha u lost noob idiot")
##    else:
##        await ctx.send("u won the battle!")
##
##        seconds, func, ctx, playerins, dmg, mob):
        


#admin commands
@client.command()
async def cmd(ctx, *, arg):
    if str(ctx.author.id) not in admin:
        await ctx.send("Not enough permissions! Admin only.")
        return
    try:
        try:
            eval(f"{arg}")
        except:
            exec(f"{arg}")
        await ctx.send("Command executed.")
    except Exception as e:
        embed = discord.Embed(title = "**Exception**")
        embed.add_field(name = "\u200b", value = e)
        await ctx.send(embed=embed)
    
@client.command()
async def admingold(ctx, member : discord.Member, gold : int):
    if str(ctx.author.id) not in admin:
        await ctx.send("Sorry! You do not have permission.")
        return
    try:
        playerins = players[f'{member.id}']
        playerins.gold += gold
        if playerins.guild != None:
            playerins.guildins.value+=gold
        await ctx.send(f"Gave {gold} gold to {member.name}")
    except:
        await ctx.send("Error! `,admingold @ user (amount of gold)`")
        
@client.command()
async def systemban(ctx, member : discord.Member, *, reason):
    if str(ctx.author.id) not in admin:
            await ctx.send("Sorry! You do not have permission.")
            return
    elif str(member.id) in banned:
            await ctx.send("This user is already banned!")
            return
    playerins = players[str(member.id)]
    if not playerins.guild:
        for i in playerins.guild.members:
            memberins = players[i]
            memberins.guild = None
            memberins.guildpos = None
            memberins.guildins = None
                                    
        del guilds[playerins.guild]
        playerins.guild = None
        playerins.guildpos = None
        playerins.guildins = None
    elif not playerins.party:
        for i in playerins.party.members:
            memberins = players[i]
            memberins.party = None
        playerins.party = None
    
    try:
        banned[str(member.id)] = players[str(member.id)]
    except:
        banned[str(member.id)] = None
                    
    today = datetime.now()
    banperson = ctx.author.name + ctx.author.discriminator
    banpersonid = str(ctx.author.id)
    today = today.strftime("%A %d %B %Y %I:%M %p")
    baninfo[str(member.id)] = [reason, today, banperson, banpersonid]
                    
                    
@client.command()
async def adminsave(ctx):
    if str(ctx.author.id) not in admin:
        await ctx.send("Sorry! You do not have permission.")
        return
    fm.save(data)
    await ctx.send("Saved!")

@client.command()
async def forceheal(ctx):
    if str(ctx.author.id) not in admin:
        await ctx.send("Sorry! You do not have permission.")
        return
    playerins = players[str(ctx.author.id)]
    playerstats = playerins.stats
    playerstats['hp'] = playerstats['maxhp']
    await ctx.send('You have been healed by magical powers!')

@client.command()
async def grant(ctx, member : discord.Member, *, status):
    if str(ctx.author.id) not in admin:
        await ctx.send("Sorry! You do not have permission to do this.")
        return
    memberins = players[f'{member.id}']
    memberins.status = status
    await ctx.send(f"Player '{memberins.user}' was conferred the role of '{status}'")

@client.command()
async def reload(ctx):
    if str(ctx.author.id) not in admin:
        await ctx.send("Sorry! You do not have permission to do this.")
        return
    fm.save(data)
    open('data.FM', 'wb').close()
    data = fm.load("data")
    banned = data.chooseobj("banned") # dictionary of banned playerids
    races = data.chooseobj("races")
    admin = data.chooseobj("admins") # list of admin ids
    players = data.chooseobj("players")
    tinteraction = data.chooseobj("tinteraction") # dict {'coords' : {'npc or locations' : {discord.Embed, 'paths'}}
    playerlist = list(players)
    map_ = data.chooseobj("map") # nested list
    baninfo = data.chooseobj("baninfo") #dict {'playerid' : [banreason, date of ban, banned by who]}
    places = data.chooseobj("places")
    skills = data.chooseobj("skills")
    levels = data.chooseobj("levels")
    locationinfo = data.chooseobj("locationinfo") # dict {'coords' : discord.Embed}
    mobs = data.chooseobj("mobs") #{1 : {mob : [minlevel, maxlevel, multiplier, phys_atk, mag_atk, phys_def, mag_def, cooldown]}}
    guilds = data.chooseobj("guilds") # dict {'guildname' : guild instance}
    gear = data.chooseobj("gear")   


client.run(TOKEN)
