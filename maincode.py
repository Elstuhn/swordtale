#make storage unit for adventure cards for adventurers guilds
import discord
from discord.ext import commands, tasks
from discord.ext.commands.bot import AutoShardedBot
from discord.ext.commands.core import check
import time
import typing as t
from time import sleep
import os
import pickle
import asyncio
import random
from datetime import datetime
from collections import defaultdict
import atexit
import functools
#calculate function so that damage values can be changed in the middle of battle 
#instantiation
areas = {'3506': 'starting'}
fileopened = {}
''''
Things to note:
-For skills, dont make boosts too high
-For mobs, dont make stats too high (physatk, phys_def, magatk, magdef)
'''
def root(number, n : int = 2):
    return number**(1/n)

class Player(): #Player Class
    def __init__(self, username, race):
        self.user = username
        self.race = race
        self.inventory = defaultdict(int) #(key=class repr, value = amount)
        self.gear = {"weapon" : None, "secondary" : None, "helmet" : None, "chestplate" : None, "leggings" : None, "boots" : None, "ring" : None, "amulet" : None, "special" : None}
        self.gold = 0
        self.level = 0
        self.exp = 0
        self.guild = None #guildname
        self.guildpos = None #guild position
        self.guildins = None #guildinstance
        self.party = None    #party instance
        self.statsp = {'maxhp' : 1, 'agility' : 1, 'atk': 1, 'defense' : 1, 'phys_atk' : 1, 'phys_def' : 1, 'mag_def' : 1, 'mag_atk' : 1, 'looting' : 1, 'cooldown_speed' : 1}
        self.stats = {'maxhp' : 20, 'hp' : 20, 'agility' : 1, 'atk': 5, 'defense' : 2, 'phys_atk' : 1, 'phys_def' : 1, 'mag_def' : 1, 'mag_atk' : 1, 'looting' : 1, 'cooldown_speed' : 0}
        self.class_ = None
        self.skills = {"e" : [0, 0, 'Beginner', 'punch', 1, 1, {}, 5]} #index 0: times used, index 1: level, index 2: level name, index 3: skill name, 4: phy_atk multiplier, 5: mag_atk multiplier 6: {'buffname' : [seconds, {'buffs'('statname': percentage)}]} 7: cooldown time(seconds)
        self.location = ["4-4", "Agelock Town - It seems like time slows down in this town?"]
        self.fightstat = None #In fight (if not, None, else, True)
        self.status = "Adventurer"
        self.advcard = None
        self.quests = {}
        self.points = 0
        self.proc = False #states if user is in a process or not

class Adventurers_Guild():
    '''
    Adventurer's Guild for adventurers to get quests and get gold and rewards for completing them
    questlist has to be randomized every 12 hours as well with a limit of 8 quests
    '''
    def __init__(self):
        self.questlist = {}
        self.members = {}
        
    def register(self, playerins):
        card = Adventurers_Card(playerins)
        playerins.advcard = card
        self.members[str(playerins.user)] = card
    
    def givequest(self, playerins):
        ## MARK: - TODO
        pass

class Adventurers_Card():
    def __init__(self, userins):
        self.ownerins = userins #player instance
        self.owner = userins.user #name of owner
        self.rank = "F"
        self.quests = {}
        self.questcount = 0
        self.title = None
        self.kills = 0
    
    def check_rank(self, rank):
        return self.rank == rank
    
    def updaterank(self):
        #check if requirements fulfilled: TODO
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

class Guild:
    def __init__(self, name : str, owner : str):
        self.name = name
        self.owner = owner # ctx.author.id in str form
        self.value = data.chooseobj('players')[f'{owner}'].gold #set initial guild value to owner's gold amount
        self.members = {} #memberid : membername
        self.roles = {'Guild Master' : guildmaster, 'Member' : member}
        self.rolepos = ['Guild Master', 0, 0, 0, 0, 0, 'Member']
        self.allies = {}
        self.enemies = {}

class Shop:
    def __init__(self, owner, shop : dict):
        self.owner = owner
        self.shop = shop #dict{item instance : cost}

    def embed(self):
        embed = discord.Embed(title = f"**__{self.owner}'s Shop__**")
        embed.add_field(name = "\u200b", value = "\u200b", inline=False)
        for num, item in enumerate(self.shop):
            embed.add_field(name = f"**{num}. {item}**  {self.shop[item]}:coin:", value = f"*{item.lore}*", inline=False)
        return embed

class Mob():
    def __init__(self, name, level = 1, atk = 1, hp = 1, defense = 1, agility = 1, phys_atk = 1, phys_def = 1, mag_atk = 1, mag_def = 1, cooldown_speed = 4, multiplier = 1): #atk, defense, hp will be calculated as constant*multiplier
        self.name = name
        self.level = level
        self.atk = atk
        self.hp = hp
        self.defense = defense
        self.agility = agility
        self.phys_atk = phys_atk
        self.phys_def = phys_def
        self.mag_atk = mag_atk
        self.mag_def = mag_def
        self.cooldown = cooldown_speed
        self.multiplier = multiplier


class Gear():
    def __init__(self, name : str, lore : str, emoji : str, type_ : str, hp : int = 0, atk : int = 0, defense : int = 0, agility : int = 0, phys_atk : int = 0, phys_def : int = 0, mag_atk : int = 0, mag_def : int = 0, looting : int = 0):
        self.name = name
        self.lore = lore
        self.emoji = emoji
        self.type_ = type_
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.agility = agility
        self.phyatk = phys_atk
        self.phydef = phys_def
        self.magatk = mag_atk
        self.magdef = mag_def
        self.looting = looting
        self.dict_ = {
            'hp' : self.hp,
            'atk' : self.atk,
            'defense' : self.defense,
            'agility' : self.agility,
            'phy_atk' : self.phyatk,
            'phy_def' : self.phydef,
            'mag_atk' : self.magatk,
            'mag_def' : self.magdef,
            'looting' : self.looting
        }
    
    def __str__(self):
        return f"(name={self.name}, lore = {self.lore}, emoji = {self.emoji}, type = {self.type_}, hp = {self.hp}, atk = {self.atk}, defense = {self.defense}, agility = {self.agility}, phyatk = {self.phyatk}, phydef = {self.phydef}, magatk = {self.magatk}, magdef = {self.magdef})"
        
    def __repr__(self):
        return self.name
    
        
class Item():
    def __init__(self, name, lore):
        self.name = name
        self.lore = lore

class Consumable():
    def __init__(self, name, lore, emoji = '', hp = 0, atk = 0, defense = 0, agility = 0, phys_atk = 0, phys_def = 0, mag_atk = 0, mag_def = 0, looting=0):
        self.name = name
        self.lore = lore
        self.emoji = emoji
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.agility = agility
        self.physatk = phys_atk
        self.physdef = phys_def
        self.magatk = mag_atk
        self.magdef = mag_def
        self.looting = looting
        self.dict_ = {
            'hp' : self.hp,
            'atk' : self.atk,
            'defense' : self.defense,
            'agility' : self.agility,
            'phys_atk' : self.physatk,
            'phys_def' : self.physdef,
            'mag_atk' : self.magatk,
            'mag_def' : self.magdef,
            'looting' : self.looting
        }
        
    def __str__(self):
        return f"(name={self.name}, lore = {self.lore}, emoji = {self.emoji}, stats = {self.dict_}"
    
    def __repr__(self):
        return self.name

class Error(Exception):
    """Base class for other exceptions"""
    pass

class EndProcess(Error):
    """For the three battling functions"""
    pass

from FileMonster import *
#data loading
fm = FileMonster()
data = fm.load("data")
banned = data.chooseobj("banned") # dictionary of banned playerids
races = data.chooseobj("races")
admin = data.chooseobj("admins") # list of admin ids
players = data.chooseobj("players")
tinteraction = data.chooseobj("tinteraction") # dict {'coords' : {'npc or locations' : {discord.Embed, 'paths'}}
playerlist = [players[p].user for p in players]
map_ = data.chooseobj("map") # nested list
baninfo = data.chooseobj("baninfo") #dict {'playerid' : [banreason, date of ban, banned by who]}
places = data.chooseobj("places")
skills = data.chooseobj("skills")
levels = data.chooseobj("levels")
locationinfo = data.chooseobj("locationinfo") # dict {'coords' : discord.Embed}
mobs = data.chooseobj("mobs") #{1 : {mob : [minlevel, maxlevel, multiplier, phys_atk, mag_atk, phys_def, mag_def, cooldown]}}
guilds = data.chooseobj("guilds") # dict {'guildname' : guild instance}
gears = data.chooseobj("gear")
ul = data.chooseobj('update')
ag = data.chooseobj('ag')
shops = data.chooseobj('shops')

#setup begin
with open('token', 'rb') as readfile:
    TOKEN = pickle.load(readfile)

intents = discord.Intents.all()

##client = discord.Client(activity = discord.Game(name=",help"))
client = commands.Bot(command_prefix = ",", activity = discord.Game(name=",help"), intents=intents, help_command = None)

ag = Adventurers_Guild()
guildmaster = Role('Guild Master', 0, kickPerms = True, invitePerms = True, setrolePerms = True, rolecreationPerms = True, editPerms = True)
member = Role('Member', 6)

        

async def checkstart(ctx, game = False, private = False, fighting = False, proccheck = False) -> bool:
    """
    to check if bot should reply to player's sent command or not
    if return value is false, bot doesn't reply to player else bot carries out function
    Game = True means check for if player has a profile or not
    private = True means the command can be used in DMs
    fighting = True means check for if user is fighting, if he is return False
    proccheck = True means check if a player is in any processes at all
    """
    channel = ctx.channel.type
    channel = str(channel)
    name = ctx.author.name
    authorid = str(ctx.author.id)
    if authorid in banned:
        await ctx.send("Sorry! You are banned.")
        return False
    
    elif channel == "private" and not private:
        return False
    
    elif authorid not in players and game:
        embed = discord.Embed("You haven't started your adventure yet! Start it with `,start`")
        await ctx.send(embed=embed)
        return False

    elif fighting and players[f'{authorid}'].fightstat:
        embed = discord.Embed(title = "**You're currently in a fight!**")
        await ctx.send(embed=embed)
        return False
     
    elif proccheck and players[f'{authorid}'].proc:
        embed = discord.Embed(title = "**Focus on what you are doing!**")
        await ctx.send(embed=embed)
        return False

    else:
        return True

def systemcheck(game = False, private = False, fighting = False, proc=False):
    def wrap(func):
        @functools.wraps(func)
        async def wrapped(ctx, *args, **kwargs):
            check = await checkstart(ctx, game, private, fighting, proc)
            if not check:
                return
            else:
                returnvalue = await func(ctx, *args, **kwargs)
                return returnvalue
        return wrapped
    return wrap

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

#Normal bot commands
@client.command()
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
@systemcheck()
async def help(ctx):
    await ctx.trigger_typing()
    embedVar = discord.Embed(title = "General Commands List")
    embedVar.add_field(name = ",help", value = "Shows this lol", inline=False)
    embedVar.add_field(name = ",invite", value = "Gets the invite link of the bot", inline=False)
    embedVar.add_field(name = ",server", value = "Gets information on the server", inline = False)
    embedVar.add_field(name = ",purge (messages)", value = "Purges an amount of messages given that you have the correct permissions", inline = False)
    embedVar.add_field(name = ",gamehelp", value = "Shows game related commands", inline=False)
    embedVar.add_field(name = ",guildhelp", value = "Shows guild related commands", inline=False)
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
    embed.add_field(name = ",guildhelp", value = "shows all the commands in relation to guilds", inline = False)
    embed.add_field(name = ",advhelp", value = "Looks at commands for adventurers guild", inline=False)
    embed.add_field(name = ",start", value = "starts your adventure", inline= False)
    embed.add_field(name = ",player @user", value = "shows your player info if either you or no one was tagged", inline= False)
    embed.add_field(name = ",stats", value = "shows your stats", inline = False)
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
    embed.add_field(name = ",recover", value = "Recover your hp for free", inline=False)
    embed.add_field(name = ",explore", value = "Battle a random mob. Can only be used inthe wild", inline=False)
    embed.add_field(name = ",ul", value = "Shows the log for the latest updates", inline=False)
    embed.add_field(name = ",equip (slot number)", value = "Equips the gear in the player's inventory corresponding to the slot number specified in argument", inline=False)
    embed.add_field(name = ",assignpoints", value = "Assign your leftover points to different stats", inline=False)
    embed.add_field(name = ",pay @user (amount)", value = "pays a user gold", inline=False)
    embed.add_field(name = ",showpoints", value="Shows how much points you have left in your profile", inline=False)
    embed.add_field(name = ",lb", value = "Shows the top players", inline=False)
    embed.add_field(name = ",rlb", value = "Shows the top richest players", inline=False)
    embed.add_field(name = ",itemshow (slot number)", value = "Shows information for the gear", inline=False)
    embed.add_field(name = ",advguild", value = "Interacts with the Adventurer's Guild", inline=False)
    embed.add_field(name = ",gvlb", value = "Looks at top 10 richest guilds", inline=False)
    embed.colour = discord.Colour.random()
    await ctx.send(embed = embed)

@client.command()
async def advhelp(ctx):
    embed = discord.Embed(title = "**Adventurer's Guild Commands**")
    embed.add_field(name = ",advcard", value = "Shows your adventurer's card", inline=False)
    

@client.command()
async def start(ctx):
    """
    Commmand used to start playing the game
    """
    check = await checkstart(ctx, private = True)
    if not check:
        return
    def checknum(message):
        return all([
            message.author == ctx.author,
            message.content in ['1', '2', '3', '4', '5']
        ])
    def check(message):
        return message.author == ctx.author
    if str(ctx.author.id) in players:
        await ctx.send("You already have a save! Are you sure you want to create a new save? [y/n]")
        playerins = players[f'{ctx.author.id}']
        try:
            _ = await client.wait_for("message", check=check, timeout = 20)
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
            else:
                del players[f'{ctx.author.id}']
            
        except asyncio.TimeoutError as e:
            await ctx.send("You took too long")
            return

            
    await ctx.send("You can do this tutorial in DMs, it might be better, continue? (enter 'yes' or 'no' in chat)")
    try:
        _ = await client.wait_for("message", check= check, timeout = 15)

    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return
    _ = _.content
    if _.lower() != "yes":
        await ctx.send("Tutorial cancelled. Type `,start` in my DMs if you wish to conduct the tutorial in DMs.")
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
        number = await client.wait_for("message", check=checknum, timeout = 180)
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
        playername = await client.wait_for("message", check=check, timeout = 45)
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
    elif playername in playerlist:
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
async def moneyround(money : t.Any): #money is either int or str
    if type(money) == str:
        money = int(money)
    if money//1000000000 > 0:
        return f"{round(money/1000000000, 1)}B"
    elif money//1000000 > 0:
        return f"{round(money/1000000, 1)}M"
    elif money//1000 > 0:
        return f"{round(money/1000, 1)}K"
    else:
        return str(money)

async def rewards(ctx, playerins, mobins, area):
    '''
    A function to give players rewards(exp, gold, items)
    when they win a battle
    '''
    expgain = round(6*mobins.level)
    expgain += round((expgain/100)*playerins.statsp['looting'] + playerins.stats['looting'])
    if playerins.level == 14:
        expgain = 0
    goldgain = round(9*mobins.level)
    if playerins.guild:
        playerins.guildins.value += goldgain
    stats = playerins.stats
    looting = stats['looting']
    lootcheck = random.random()
    embed = discord.Embed(title = f"**__:gift: {playerins.user}'s Loot Status :gift:__**")
    embed.add_field(name = "**Money Gained:**", value = f"{goldgain}:coin:", inline=True)
    embed.add_field(name = "**Exp Gained:**", value = f"{expgain}:green_circle: ")
    curgear = gears[area]
    if lootcheck <= 0.7 + (stats['looting']/300):
        try:
            category = random.choice([k for k in curgear if k != 'special'])
            lootname = random.choice([k for k in curgear[category]])
            lootins = curgear[category][lootname]
            embed.add_field(name = "**Item Found:**", value = f"{lootname} {lootins.emoji}")
            await addstuff(playerins, [lootins])
        except:
            pass
    elif lootcheck >= 0.95 - (stats['looting']/300):
        try:
            curgear = gears['special']
            category = curgear[mobins.name] #returns a list of gearins
            lootins = random.choice(category)
            embed.add_field(name = "**Item Found:**", value = f"{lootins.name} {lootins.emoji}")
            await addstuff(playerins, [lootins])
        except:
            pass
    playerins.gold += goldgain
    playerins.exp += expgain
    levelup = await levelcheck(ctx, playerins)
    await ctx.send(embed=embed)

async def givepoints(ctx, playerins, member : discord.Member):
    def check(message):
        return member == message.author
    def checknumber(message):
            return all([
                message.author == ctx.author,
                message.content.isdigit()
            ])
    points = playerins.points
    while True:
        if not points:
            embed = discord.Embed(title = "You've used up all your points!")
            await ctx.send(embed=embed)
            playerins.proc = False
            return 
        embed = discord.Embed(title = f"**You have {points} points left to spend, which stat would you like to invest it to?**")
        embed.add_field(name = "List of stats", value = "\u200b", inline=False)
        stats = [i for i in playerins.stats if i not in ['cooldown_speed', 'hp']]
        for i in stats:
            embed.add_field(name = f"*{i}*", value = "\u200b", inline=False)
        embed.set_footer(text = 'Type the name of the stat in the chat (enter "cancel" in the chat to cancel, you can still use the points whenever you wish to)')
        await ctx.send(embed=embed)
        try:
            message = await client.wait_for('message', check=check, timeout=120)           
        except asyncio.TimeoutError as e:
            await ctx.send("You took too long!")
            playerins.proc = False
            return
        message = message.content.lower()
        if message == 'cancel':
            embed = discord.Embed(title = "Cancelled. Remaining points put into your account.")
            embed.set_footer(text = "You can always use those points again with ,assignpoints")
            await ctx.send(embed=embed)
            playerins.proc = False
            return
        elif message not in stats:
            embed = discord.Embed(title = "That is not a valid stat name!")
            await ctx.send(embed=embed)
            sleep(0.5)
            continue
        embed = discord.Embed(title = "How many points would you like to put into this stat?")
        embed.set_footer(text = f'Answer in the chat. (You have {points} left)') 
        await ctx.send(embed=embed)
        try:
            number = await client.wait_for('message', check=checknumber, timeout = 120)
        except asyncio.TimeoutError:
            await ctx.send("You took too long!")
            return
        number = int(number.content) 
        if number <= 0:
            embed = discord.Embed("It's not gonna work.")
            await ctx.send(embed=embed)
            return 0
        elif number > points:
            embed = discord.Embed(title="Calm down Bucko, you don't have that many points.")
            await ctx.send(embed=embed)
            return 0
        playerins.points -= number
        points -= number
        playerins.stats[f'{message}'] += number
        embed = discord.Embed(title = f"**{number} points assigned to {message}**")
        embed.colour = discord.Colour.green()
        await ctx.send(embed=embed)        

async def levelcheck(ctx, playerins):
    if playerins.level == 14:
        return 0
    while True:
        requiredexp = levels[playerins.level]
        if not playerins.exp >= requiredexp:
            break
        prevlevel = playerins.level
        playerins.level += 1
        playerins.exp -= requiredexp
        embed = discord.Embed(title = "**__You've leveled up!__**")
        embed.add_field(name = f"**Previous Level: {prevlevel}**", value = f"**New Level: {playerins.level}**", inline=True)
        await ctx.send(embed=embed)
        playerins.points += 10
    await givepoints(ctx, playerins, ctx.author)

async def evalarea(playerins):
    playercoord = playerins.location[0].split('-')
    coord1 = int(playercoord[0])
    coord2 = int(playercoord[1])
    for check in areas:
        if all([
            coord1 >= int(check[0]),
            coord1 <= int(check[1]),
            coord2 >= int(check[2]),
            coord2 <= int(check[3])
        ]):
            return areas[check]
    return 0

async def addstuff(playerins, stuff : list): 
    for i in stuff: #i will be Gear instances
        playerins.inventory[i] += 1

async def randmob(playerins, area):
    """
    generate a random mob based on location
    """
    coords = playerins.location[0]
    coords = coords.split('-')
    coord1 = int(coords[0])
    coord2 = int(coords[1])
    mob = mobs[area]
    mobchoice = random.choice(list(mob))
    mobins = mob[mobchoice]
    moblevel = random.randint(mobins[0], mobins[1])
    multiplier = mobins[2]
    atk = round(3.4*moblevel*multiplier)
    hp = round(12*moblevel*multiplier)
    defense = round(1.15*moblevel*multiplier)
    phys_atk = round(mobins[3]*moblevel*1.03)
    phys_def = round(mobins[4]*moblevel*1.05)
    mag_atk = round(mobins[5]*moblevel)
    mag_def = round(mobins[6]*moblevel)
    agility = round(mobins[7]*moblevel)
    cooldown = mobins[8]
    mob = Mob(mobchoice, moblevel, atk, hp, defense, agility, phys_atk, phys_def, mag_atk, mag_def, cooldown, multiplier)
    return mob
    
async def monsterattack(ctx, playerins, mob):
    """
    calculates mob damage done and subtracts that from player's hp
    sends an embed object back to show how much health each of them has left
    """
    playerdodge = random.random()
    gearvalue = await gearvalues(playerins)
    if playerdodge >= (0.993 -(playerins.stats['agility']+gearvalue['ag'])/120):
        dmg = 0
        embed = discord.Embed(title =f"**__{playerins.user}'s Battle Status__**", description = f"You dodged the attack!")
    else:
        dmg = await calcmobdmg(playerins, mob)
        embed = discord.Embed(title =f"**__{playerins.user}'s Battle Status__**", description = f"Lvl {mob.level} {mob.name} has attacked you for {dmg} damage!")
    playerins.stats['hp'] -= dmg
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
    sleep(1.5)
    while True:
        _ = await monsterattack(ctx, playerins, mob)
        if any([playerins.stats['hp'] < 1, mob.hp < 1]):
            break
        else:
            await asyncio.sleep(seconds)
        #elif not playerins.party:
        #    return 0
            #raise EndProcess
        #else:
        #    playerins.fightstat[1] = 0
        #    members = playerins.party.members
        #    check = False
        #    for i in members:
        #        member = players[i]
        #        if member.fightstat[1]:
        #            check = True
        #            
        #    if not check:
        #        return 0
        #        #raise EndProcess
        #    else:
        #        index = alive.index(playerins)
        #        del alive[index]
        #        playerins = random.choice(alive)
    return 0
          
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
    totalphyatk = totallooting = totalmagdef = totalag = totalatk = totaldef = totalphydef = totalmagatk = 1    
    for i in playergear:
        gear = playergear[i]
        if not gear:
            continue
        totalatk += gear.atk
        totalphyatk += gear.phyatk
        totalmagdef += gear.magdef
        totalmagatk += gear.magatk
        totalphydef += gear.phydef
        totaldef += gear.defense
        totalag += gear.agility
        totallooting += gear.looting
    
    return {'atk' : totalatk,
            'phyatk' : totalphyatk,
            'phydef' : totalphydef,
            'magatk' : totalmagatk,
            'magdef' : totalmagdef,
            'def' : totaldef,
            'ag' : totalag,
            'looting' : totallooting
            }

async def calcplayerdmg(playerins, mobins, skillphyatk, skillmagatk):
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
    gearphyatk = gearvalue['phyatk']
    gearmagatk = gearvalue['magatk']
    gearatk = gearvalue['atk']
    gearag = gearvalue['ag']
    playerag = (root(playerstats['agility'], 5)*gearag)/(2800-playerins.statsp['agility']*2) 
    normalattack = default(root(gearatk, 1.8)*root(playerstats['atk'], 4)-mobins.defense*(1.1-playerag))
    phyatk = default(root(gearphyatk)*root(playerstats['phys_atk'], 4)-(mobins.phys_def*(1.1-playerag)))
    magatk = default(root(gearmagatk)*root(playerstats['mag_atk'], 4)-(mobins.mag_def*(1.1-playerag)))
    playerdmg = magatk+phyatk+normalattack 
    return playerdmg

async def calcmobdmg(playerins, mobins):
    '''
    calculates the true damage a mob does
    '''
    def default(value : float) -> int:
        if value <= 0:
            return 1
        else:
            return round(value)
    mobag = mobins.agility/150
    gearvalue = await gearvalues(playerins)
    gearphydef = gearvalue['phydef']
    gearmagdef = gearvalue['magdef']
    geardef = gearvalue['def']
    playerstats = playerins.stats
    mobmulti = mobins.multiplier
    mobatk = default((mobins.atk*mobmulti)-((root(playerstats['defense'], 4))*root(geardef, 1.9)*(1.05-mobag)))
    phyatk = default((mobins.phys_atk*mobmulti)-(root(playerstats['phys_atk'], 4)*root(gearphydef, 2)*(1.10-mobag)*0.9))
    magatk = default((mobins.mag_atk*mobmulti)-(root(playerstats['mag_def'], 4)*root(gearmagdef, 2)*(1.05-mobag)*0.9))
    mobdmg = mobatk+phyatk+magatk
    return default(mobdmg)
        
            
async def messageattack(ctx, check ,buffs, mobins): #if partymembers != None, Party instance
    """
    waits for player to send a message and check if its a valid move then does some calculation and subtracts that
    from monster's health and displays in an embed object the skill used and health of both entities or if 
    player is in a party, mob and all players' hp then add the buffs given by the used skill to the player
    """
    playerins = players[str(ctx.author.id)]
    partymembers = playerins.party
    while True:
        if playerins.stats['hp'] <= 0:
            return 0
        try:
            _ = await client.wait_for("message", check = check, timeout = 540)

        except asyncio.TimeoutError as e:
            await ctx.send("You took too long thus the battle has ended you slowpoke.")
            if not partymembers:
                playerins.stats['hp'] = 0
            else:
                for i in partymembers.members:
                    playerins = players[i]
                    playerins.stats['hp'] = 0
            return 0
        playerins = players[str(_.author.id)]
        _ = _.content.lower()
        #ctx might not be referring to the sender of the message
        skillinfo = playerins.skills[_]
        skillname = skillinfo[3]
        mag_atk = skillinfo[5]
        phys_atk = skillinfo[4]
        skillbuff = skillinfo[6]
        dmg = await calcplayerdmg(playerins, mobins, phys_atk, mag_atk)
        for i in skillbuff: #i = buff name
            if i in list(buffs): #buffs dont stack
                continue
            addbuff = []
            for j in skillbuff[i][1]:
                originalstat = playerins.stats[j]
                playerins.stats[j] *= skillbuff[i][1][j] #multiplies player's current specific stats with the multiplier 
                difference = playerins.stats[j] - originalstat #states the diffrence in numerical value
                addbuff.append(f'{j}:{difference}')
            
            buffs[i] = [' '.join(addbuff)] + [backgroundtime, skillbuff[i][0]]
        mobins.hp -= dmg
        embed = discord.Embed(title =f"**__{playerins.user}'s Battle Status__**", description = f"You used {skillname} to deal {dmg} damage to the monster!")
        embed.add_field(name = f"**__Lvl {mobins.level} {mobins.name}__**", value = "\u200b", inline=False)
        embed.add_field(name=f"**Health :heart: {mobins.hp}**", value = "\u200b", inline=False)
        embed.add_field(name = "\u200b", value = "\u200b", inline=False)
        embed.add_field(name = f"**__{playerins.user}__**", value = "\u200b", inline=False)
        embed.add_field(name = f"**Health :heart: {playerins.stats['hp']}**", value = "\u200b", inline=False)
        await ctx.send(embed=embed)
        if mobins.hp < 1:
            return 0
                
        #except:
        #    await ctx.send("Skill not found!")

        await asyncio.sleep(0.5)

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
            mob.hp < 1,
            eval(checkdead)
            ]):
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
        await asyncio.sleep(0.5)
    mobattack.cancel()
    checkmessage.cancel()
    return 0

async def singlebattle(ctx, check, area):
    '''
    Function for letting players battle with monsters. Only works with one person.
    Anyone in a party is not allowed to battle
    '''
    def checkverify(message):
        return all([
            message.author == ctx.author,
            any([
                message.content.lower() == 'yes',
                message.content.lower() == 'no'
                ])
        ])
    playerins = players[f'{ctx.author.id}']
    mobins = await randmob(playerins, area)
    embed = discord.Embed(title=f"**You are about to fight lvl {mobins.level} {mobins.name}**")
    embed.add_field(name = "Would you like to battle it?", value = "*yes/no*")
    embed.set_footer(text = "type your answer in chat")
    embed.colour = discord.Colour.red()
    await ctx.send(embed=embed)
    try:
        message = await client.wait_for('message', check=checkverify, timeout = 60)
    except asyncio.TimeoutError:
        await ctx.send("You took too long!")
        playerins.fightstat = None
        playerins.proc = False
        return
    message = message.content
    if message.lower() == "no":
        number = random.random()
        if number <= 0.8: #80%
            embed = discord.Embed(title = "**You've Escaped!**")
            await ctx.send(embed= embed)
            playerins.fightstat = None
            return
        else:
            embed = discord.Embed(title = "**You failed to escape!**")
            embed.colour = discord.Colour.red()
            await ctx.send(embed=embed)
    
    #mobdamaging = await returntaskmobattack(ctx, playerins, mobins)
    embed = discord.Embed(title = "**Battle Started!**")
    await ctx.send(embed=embed)
    mobdamaging = asyncio.ensure_future(taskbattle(ctx, playerins, mobins))
    buffs = {}
    checkmessage = asyncio.ensure_future(messageattack(ctx, check, buffs, mobins))
    checksecond = asyncio.ensure_future(secondcheck(ctx, mobdamaging, checkmessage, mobins, playerins, buffs))
    try:
        await mobdamaging
        await checksecond
        await checkmessage
    except:
        pass
    embed = discord.Embed(title = "**__Battle Outcome__**")
    if playerins.stats['hp'] <= 0:
        embed.add_field(name = f"**:poop: You lost to level {mobins.level} {mobins.name} :poop:**", value = "\u200b", inline=False)
    else:
        embed.add_field(name = f"**:tada: You won the battle against level {mobins.level} {mobins.name} :tada:**", value = "\u200b", inline = False)
        if playerins.advcard:
            playerins.advcard.kills+=1
        await rewards(ctx, playerins, mobins, area)
    playerins.fightstat = None
    playerins.proc = False
    await ctx.send(embed=embed)
    
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
@systemcheck(game=True, proc=True)
async def create_guild(ctx, *, guildname):
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
@systemcheck(game=True, proc=True)
async def guildsetrole(ctx, member : discord.Member, *,  role):
    """
    allows user to edit a specific guild-role's permissions
    """
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
    embed.add_field(name = ",gcreate (guild name)", value = "creates a guild (requires 4k gold)")
    embed.add_field(name= ",guild @user", value = "shows your own guild info if you didnt tag anyone", inline=False)
    embed.add_field(name = ",ginvite @user", value = "invites someone to your guild")
    embed.add_field(name = ",gleave", value = "leaves the guild you are in", inline = False)
    embed.add_field(name=",gdisband", value = "disbands the guild(must be guild master)")
    embed.add_field(name = ",gset @user (role)", value = "sets guild member's rank to the role specified (must have permissions)(case sensitive)", inline=False)
    embed.add_field(name = ",gcreaterole (role)", value = "creates a new guild role (must have permissions)", inline=False)
    embed.add_field(name = ",geditrole (role)", value = "edits a role's permissions", inline=False)
    embed.add_field(name = ",gmembers", value = "displays all members of the guild you are in ", inline = False)
    await ctx.send(embed=embed)

@client.command(aliases = ["guildinfo"])
@systemcheck(game=True)
async def guild(ctx, member : discord.Member = 0):
    if not member:
        member = ctx.author
    playerins = players[f'{member.id}']
    if playerins.guild == None:
        await ctx.send("You're not in a guild!")
        return
    guild = playerins.guildins
    embed = discord.Embed(title = f"**__{playerins.guild}__**")
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    owner = players[guild.owner].user
    embed.add_field(name = "Guild Master :crown:", value = f"{owner}")
    embed.add_field(name = "Value :moneybag:", value = f"{await moneyround(guild.value)}")
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
    embed.set_footer(text = f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.send(embed = embed)

@client.command(aliases = ["ginv"])
@systemcheck(game=True, proc=True)
async def ginvite(ctx, member : discord.Member):
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
@systemcheck(game=True, proc = True)
async def gdeleterole(ctx, *, role):
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
@systemcheck(game=True, proc=True)
async def gmembers(ctx):
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
@systemcheck(game=True, proc=True, fighting=True)
async def gleave(ctx):
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
    rolename = rolename.strip().lower()
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
        return all([
            message.author == ctx.author,
            any([
                message.content.strip().lower() in ['kick', 'invite', 'setrole', 'rolecreation', 'edit'],
                message.content.split()[0].lower() == 'name'
            ])
        ])
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
            _ = _.strip().lower()
            splitted = _.split()
            if _.lower() == "cancel":
                await ctx.send("Cancelled.")
                return
            elif splitted[0] == "name":
                newname = ' '.join(splitted[1:])
                del guildins.roles[roleins.name]
                roleins.name = newname
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
@systemcheck(game=True)
async def itemshow(ctx, slotnum):
    playerins = players[str(ctx.author.id)]
    inventory = playerins.inventory
    slot = int(slotnum)
    if len(inventory) < slot+1 or slot < 0:
        embed = discord.Embed(title = "**There are no such existing slots in your inventory!**")
        await ctx.send(embed=embed)
        return
    count = 0
    for i in inventory:
        if count == slot:
            item = i #item will be Gear instance
            print(item)
            break
        count+=1
    embed = discord.Embed(title = f"**__{item.name} Information__**")
    embed.add_field(name = "**Name:**", value = f"{item.name}", inline=False)
    embed.add_field(name = "**Lore:**", value = f"{item.lore}", inline=False)
    embed.add_field(name = "**Type**", value = f"{item.type_}", inline=False)
    embed.add_field(name = "\u200b", value="\u200b", inline=False)
    embed.add_field(name="**__Item Stats__**", value = "\u200b", inline=False)
    embed.add_field(name = "**Hp :heart:**", value = f"{item.hp}", inline=True)
    embed.add_field(name = "**Attack :dagger:**", value = f"{item.atk}", inline=True)
    embed.add_field(name = "**Defense :shield:**", value = f"{item.defense}", inline=True)
    embed.add_field(name = "**Agility :dash:**", value = f"{item.agility}", inline=True)
    embed.add_field(name="\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "**Phys Atk**", value = f"{item.phyatk}", inline=True)
    embed.add_field(name = "**Phys Def**", value = f"{item.phydef}", inline=True)
    embed.add_field(name = "**Mag Atk**", value = f"{item.magatk}", inline=True)
    embed.add_field(name = "**Mag Def**", value = f"{item.magdef}", inline=True)
    await ctx.send(embed=embed)
    
@client.command()
@systemcheck()
async def gvlb(ctx):
    sortedguilds = sorted(guilds, key = lambda x : guilds[x].value, reverse =True)
    sortedguilds = sortedguilds[0:10]
    embed = discord.Embed(title = "**__Top Richest Guilds__**")
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "**Guild Name**", value = "\n".join([i for i in sortedguilds]))
    embed.add_field(name = "**Guild Value**", value = "\n".join([await moneyround(guilds[i].value) for i in sortedguilds]))
    await ctx.send(embed = embed)

@client.command()
@systemcheck(game=True)
async def rlb(ctx):
    people = sorted(players, key = lambda x : players[x].gold, reverse=True)
    people = people[0:10]
    embed = discord.Embed(title = "**__Top Richest Players__**")
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "**Player Name**", value = "\n".join([players[i].user for i in people]))
    embed.add_field(name = "**Player Gold**", value = "\n".join([await moneyround(players[i].gold) for i in people]))
    embed.colour = discord.Colour.random()
    await ctx.send(embed=embed)

@client.command()
@systemcheck(game=True)
async def lb(ctx):
    people = sorted(players, key = lambda x : players[x].level, reverse=True)
    people = people[0:10]
    embed= discord.Embed(title = "**__Highest Levelled Players__**")
    embed.add_field(name = "\u200b", value="\u200b", inline=False)
    embed.add_field(name = "**Player Name**", value = "\n".join([players[i].user for i in people]))
    embed.add_field(name = "**Player Level**", value = "\n".join([str(players[i].level) for i in people]))
    embed.colour = discord.Colour.random()
    await ctx.send(embed=embed)

@client.command(aliases = ['points', 'point'])
async def showpoints(ctx):
    check = await checkstart(ctx, game=True)
    if not check:
        return
    playerins = players[str(ctx.author.id)]
    embed = discord.Embed(title = f"**You currently have {playerins.points} points**")
    embed.colour = discord.Colour.random()
    await ctx.send(embed = embed)
    
@client.command(aliases = ['assignpoint'])
@systemcheck(game=True, fighting=True, proc=True)
async def assignpoints(ctx):
    playerins = players[str(ctx.author.id)]
    playerins.proc = True
    await givepoints(ctx, playerins, ctx.author)
    playerins.proc=False
    
@client.command()
@systemcheck(game=True, fighting=True)
async def pay(ctx, member : discord.Member = 0, amount : int = 0):
    playerins = players[str(ctx.author.id)]
    if member == 0:
        embed = discord.Embed(title = "Correct Usage: ,pay @user (amount)")
        await ctx.send(embed=embed)
        return 0
    elif amount <= 0:
        embed = discord.Embed(title = "You're funny.")
        await ctx.send(embed=embed)
        return
    elif member == ctx.author:
        embed = discord.Embed(title = "Stop trying to pay yourself.")
        await ctx.send(embed=embed)
        return
    elif int(amount) > playerins.gold:
        embed = discord.Embed(title = "**Bro you're not as rich as you think**")
        await ctx.send(embed=embed)
    elif str(member.id) not in players:
        embed = discord.Embed(title = f"**{member.name} does not have a profile yet!**")
        await ctx.send(embed=embed)
    memberins = players[str(member.id)]
    playerins = players[str(ctx.author.id)]
    def check(message):
        return all([
            ctx.author == message.author,
            message.content.lower() in ['yes', 'no']
        ]) 
    moneystr = await moneyround(amount)
    embed = discord.Embed(title = f"**You are about to pay {member.name} {moneystr} gold!**")
    embed.add_field(name = "Confirm?", value = "*yes/no*", inline=False)
    embed.set_footer(text = "Answer with yes or no in chat.")
    await ctx.send(embed=embed)
    try:
        message = await client.wait_for('message', check=check, timeout=110)
    except asyncio.TimeoutError:
        await ctx.send("You took too long!")
        return
    message = message.content.lower()
    if message == 'n':
        embed = discord.Embed(title = f"**You did not pay {memberins.user}. Oof.**")
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title = f"**You paid {memberins.user} {moneystr} gold!**")
    await ctx.send(embed=embed)
    memberins.gold += amount
    playerins.gold -= amount

@client.command(aliases = ['heal'])
@systemcheck(game=True, proc=True)
async def recover(ctx):
    playerins = players[str(ctx.author.id)]
    if playerins.fightstat:
        embed = discord.Embed(title="**You cannot heal in the middle of a fight!**")
        embed.colour = discord.Colour.random()
        await ctx.send(embed=embed)
        return
    playerins.stats['hp'] = playerins.stats['maxhp']
    embed = discord.Embed(title = "**You have been healed!**")
    embed.colour = discord.Colour.random()
    await ctx.send(embed=embed)

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
        if gear[i]:
            embed.add_field(name = f"{i}", value = f"{gear[i].name}", inline=False)
        else:
            embed.add_field(name = f"{i}", value = f"{gear[i]}", inline=False)
    await ctx.send(embed = embed)

@client.command()
async def equip(ctx, slot):
    playerins = players[str(ctx.author.id)]
    inventory = playerins.inventory
    slot = int(slot)
    if len(inventory) < slot+1 or slot < 0:
        embed = discord.Embed(title = "**There are no such existing slots in your inventory!**")
        await ctx.send(embed=embed)
        return
    count = 0
    for i in inventory:
        if count == slot:
            item = i #item will be Gear instance
            print(item)
            break
        count+=1
    if not isinstance(item, Gear):
        embed = discord.Embed(title = "**This item is not a valid equippable gear!**")
        await ctx.send(embed=embed)
    if not inventory[item]:
        await ctx.send("You do not have enough of this item!")
    prevgear = playerins.gear[f'{i.type_}']
    playerins.gear[f"{i.type_}"] = item
    embed = discord.Embed(title = f"**Equipped {item.name}**")
    if prevgear:
        playerins.inventory[prevgear]+=1
        embed.add_field(name = f"**Unequipped {prevgear.name}**", value = "\u200b")
    embed.colour = discord.Colour.random()
        
    playerins.inventory[item] -= 1
    if not playerins.inventory[item]:
        del playerins.inventory[item]
    await ctx.send(embed=embed)
            
@client.command(aliases = ['inventory', 'inv'])
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
    
@client.command(aliases = ['ac'])
@systemcheck(game=True, fighting=True)
async def advcard(ctx):
    playerins = players[str(ctx.author.id)]
    adcard = playerins.advcard
    embed = discord.Embed(title = f"{playerins.user}'s Adventurer Card")
    embed.add_field(name = "**Username**", value = f"{playerins.user}", inline=True)
    embed.add_field(name = "**Title**", value = f"{adcard.title}", inline=True)
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "**Rank**", value = f"{adcard.rank}", inline=False)
    embed.add_field(name = "**Quest Count**", value = f"{adcard.questcount}", inline=False)
    embed.add_field(name = "**Kills**", value = f"{adcard.kills}", inline=False)
    await ctx.send(embed=embed)

@client.command(aliases = ["ag"])
@systemcheck(game=True, proc = True)
async def advguild(ctx):
    playerins = players[str(ctx.author.id)]
    coords = playerins.location[0]
    coords = coords.split('-')
    if not map_[int(coords[0])][int(coords[1])] == 't':
        await ctx.send(f"You are not in a town <@{ctx.author.id}>!")
    playerins.proc = True
    embed = discord.Embed(title = "**__Guild Master Yuki greets you with a gentle smile and asks what you would like to do today__**")
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    embed.add_field(name = "**Options**", value = "\u200b")
    embed.add_field(name = "*1) Get your adventurer card*", value = "\u200b", inline=False)
    embed.add_field(name = "*2) Upgrade your adventurer rank*", value = "\u200b", inline=False)
    embed.add_field(name = "*3) See quests*", value = "\u200b", inline=False)
    embed.add_field(name = "*4) See shop*", value = "\u200b", inline=False)
    embed.add_field(name = "*5) Sell stuff*", value = "\u200b", inline=False)
    embed.add_field(name = "*6) Nevermind lol*", value = "\u200b", inline=False)
    embed.set_footer(text = "Enter the number of your option")
    await ctx.send(embed=embed)
    def check(message):
        return all([
            message.author == ctx.author,
            message.content in ['1', '2', '3', '4', '5']
        ])
    try:
        txt = await client.wait_for("message", check=check, timeout=50)
    except asyncio.TimeoutError:
        await ctx.send("You took too long!")
    txt = txt.content
    if txt == "1":
        if playerins.advcard:
            embed = discord.Embed(title = "**You already have an adventurer's card!**")
            embed.colour = discord.Colour.red()
            await ctx.send(embed=embed)
            playerins.proc=False
            return
        ag.register(playerins)
        embed = discord.Embed(title = "**Your adventurer's card has been created and added to your profile!**")
        embed.set_footer(text = "You can use ,advcard to see it")
        embed.colour = discord.Colour.random()
        await ctx.send(embed=embed)
        playerins.proc=False
        
    elif txt == "2":
        embed = discord.Embed(title = "**This feature isn't opened yet! Stay tuned!**")
        await ctx.send(embed=embed)
        # MARK:- TODO: Have to work on it
        
    elif txt == "3":
        embed = discord.Embed(title = "**This feature isn't opened yet! Stay tuned!**")
        await ctx.send(embed=embed)
        playerins.proc = False
    
    elif txt == "4":
        def check(message):
            return all([
                message.author == ctx.author,
                message.content.isdigit(),
                message.content.lower() == 'cancel'
            ])
        def checkemoji(reaction, user):
            return all([
                user == ctx.author,
                reaction.message == sent,
                str(reaction.emoji) in ["✅", "❌"] 
            ])
        def checknormal(message):
                return all([
                    message.author == ctx.author,
                    message.content.lower() in ['yes', 'no']
                ])
            
        try:
            shop = shops[playerins.location[0]]
        except:
            await ctx.send("The shop here isn't opened yet! Come back next time")
            playerins.proc = False
            return
        shopembed = shop.embed()
        shopdic = shop.shop
        shopembed.colour = discord.Colour.random()
        while True:
            await ctx.send(embed=shopembed)
            await ctx.send("Enter the number of the item you want or type 'cancel' to cancel")
            try:
                message = await client.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send('You took too long!')
                playerins.proc = False
                return
            if message.content.lower() == 'cancel':
                embed = discord.Embed(title = f"**{shop.owner} thanks you for visiting**")
                embed.set_footer(text = "You left the shop.")
                embed.colour = discord.Colour.random()
                await ctx.send(embed=embed)
                playerins.proc = False
                return
            message = int(message.content)
            if message > len(shopdic):
                await ctx.send("No such item!")
                continue
            count = 1
            for i in shopdic:
                if count == message:
                    item = i
                    break
                count += 1
            price = shopdic[item]
            if price > playerins.gold:
                await message.reply(content = "You don't have enough money!")
                continue
            embed = discord.Embed(title = f"Are you sure you want to buy {item} for {price}?")
            embed.set_footer(text = "Answer with yes/no in chat.")
            embed.colour = discord.Colour.random()
            await ctx.send(embed=embed)
            try:
                message = await client.wait_for('message', check=checknormal, timeout=80)
            except asyncio.TimeoutError:
                await ctx.send("You took too long!")
                playerins.proc = False
                return
            message = message.content.lower()
            if not any([message == 'no', message=='yes']):
                await message.reply(content="That's not a valid reply! (yes/no)")
                continue
            elif message == 'no':
                continue
            playerins.gold -= price
            playerins.inventory[item] += 1
            embed = discord.Embed(title = f"**You have bought {item} for {price}:coin:!**")
            embed.add_field(name = "\u200b", value = "\u200b", inline=False)
            embed.add_field(name ="Would you like to buy some more stuff?", value = "\u200b")
            embed.set_footer(text = "React with the appropriate emojis. The tick for yes and the X for no")
            sent = await ctx.send(embed=embed)
            await sent.add_reaction("✅")
            await sent.add_reaction("❌")
            try:
                reaction, user = await client.wait_for('reaction_add', check=checkemoji, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("You took too long!")
                playerins.proc = False
                return
            if reaction.emoji == "❌":
                embed = discord.Embd(title = f"**{shop.owner} bids you goodbye and good luck on your adventure.**")
                embed.set_footer(text = "You left the shop.")
                await ctx.send(embed=embed)
                break
            
        playerins.proc = False
            
            
        
    elif txt == "5":
        embed = discord.Embed(title = "**Master Brawn's Shop**")
        embed.add_field(name = "")
    else:
        embed = discord.Embed(title = "**You said goodbye to Master Brawn and he asked u to come again to give him money.**")
        await ctx.send(embed=embed)
       
@client.command(aliases = ["towninfo"])
@systemcheck(game=True, fighting=True, proc=True) 
async def tinfo(ctx):
    playerins = players[f'{ctx.author.id}']
    location = playerins.location[0]
    try:
        embed = locationinfo[location]
    except:
        embed = discord.Embed(title = "**__The Wilderness__**", description = "Just the wilderness. Where are you going?")
    embed.colour = discord.Colour.random()
    embed.set_footer(text = "Interact with different things with ,tinteract (NPC name/location name)")
    await ctx.send(embed=embed)

@client.command(aliases = ["tint", "interact"])
@systemcheck(game=True, proc=True, fighting=True)
async def tinteract(ctx, *, aim):
    playerins = players[f'{ctx.author.id}']
    coords = playerins.location[0]
    playerins.proc = True
    aim = aim.lower()
    def check(message):
        return message.author == ctx.author
    
    try:
        embeddict = tinteraction[coords][aim]
        embedlist = embeddict['first']
        embed = embedlist[0]
    except:
        embed = discord.Embed(title=f"**{aim} not found as an interactable!**")
        embed.set_footer(text = "Operation has been cancelled.")
        await ctx.send(embed=embed)
        playerins.proc = False
        return
    
    while True:
        embed.colour = discord.Colour.random()
        await ctx.send(embed = embed)
        if len(embedlist) == 1:
            playerins.proc=False
            return
        _ = await client.wait_for("message", check=check, timeout = 120)
        _ = _.content
        if _ not in embedlist:
            await ctx.send("Invalid path!")
            playerins.proc = False
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
@systemcheck(game = True, proc=True)
async def pinvite(ctx, member : discord.Member):
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
@systemcheck(game=True, proc=True, fighting=True)
@commands.cooldown(1, 15, commands.BucketType.user)
async def move(ctx, direction):
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
    embed = discord.Embed(title = f"**__{player.user}'s Stats__**\t\t\t\t   **__Class: {player.race}__**")
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

@client.command(aliases = ["playerinfo", 'profile'])
@systemcheck(game=True)
async def player(ctx, member : discord.Member = 0):
    if not member:
        member = ctx.author
    playerstat = players[f'{member.id}'] #gets player instance of sender
    embed = discord.Embed(title = f"**__{playerstat.user}'s Info__**         \t\t\t **__Status: {playerstat.status}__**")
    embed.add_field(name = "Gold :coin:", value = f"{await moneyround(playerstat.gold)}")
    embed.add_field(name = "Race :flag_white:", value = f"{playerstat.race}", inline = True)
    embed.add_field(name = "Level :arrow_up:", value = f"{playerstat.level} [{playerstat.exp}/{levels[playerstat.level]}]", inline = True)
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    adjustedcoord = playerstat.location[0].split('-')
    adjustedcoord = f"{int(adjustedcoord[0])+1}-{int(adjustedcoord[1])+1}"
    embed.add_field(name = "Co-ords :compass:", value = f"{adjustedcoord}")
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
    embed.add_field(name = "Keybind :keyboard:", value = f"{_}")
    _ = []
    t = []
    for i in playerstat.skills:
        if playerstat.skills[i] == None:
            continue
        _.append(f"{playerstat.skills[i][3]}")
        t.append(f"{playerstat.skills[i][2]}")
    _ = '\n'.join(_)
    t = '\n'.join(t)
    embed.add_field(name = "Skills :bulb:", value = f"{_}")
    _ = []
    embed.add_field(name = "Skill Mastery :low_brightness:", value = f"{t}")
    embed.colour = discord.Colour.random()
    embed.set_footer(text = f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
    await ctx.send(embed= embed)

@client.command()
@systemcheck(game=True, fighting=True, proc=True)
async def explore(ctx):
    playerins = players[f'{ctx.author.id}']
    location = playerins.location[0]
    location = location.split('-')
    area = await evalarea(playerins)
    if map_[int(location[0])][int(location[1])] == 't':
        await ctx.send("You cannot do this in a town!")
        return
    elif playerins.stats['hp'] <= 0:
        await ctx.send("Dude you don't have health.")
        return
    elif not area:
        await ctx.send("This area has not been opened yet")
        return
    #if playerins.party == None:
    #    partymembers = None
    playerins.fightstat = True
    playerins.proc = True
    def check(message):
        return all([message.author == ctx.author, message.content.lower() in players[str(ctx.author.id)].skills])
    #else:
    #    partymembers = playerins.party.members
    #    def check(message):
    #        return all([message.author in partymembers, message.content.lower() in players[str(message.author.id)].skills])
    await singlebattle(ctx, check, area)
    
@client.command(aliases = ['ul'])
async def updatelog(ctx):
    embed = discord.Embed(title = f"{ul[0]}")
    actualupdates = ul[1].split('\n')
    for i in actualupdates:
        embed.add_field(name = f"{i}", value = "\u200b", inline=False)
    embed.colour = discord.Colour.random()
    await ctx.send(embed=embed)       


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
async def adminexp(ctx, member : discord.Member, exp):
    if str(ctx.author.id) not in admin:
        await ctx.send("Sorry! You do not have permission.")
        return
    try:
        playerins = players[f'{member.id}']
        playerins.exp += int(exp)
        embed = discord.Embed(title = f"**Gave {exp} exp to {member.name}**")  
        embed.colour = discord.Colour.green()
        await ctx.send(embed=embed)   
        levelup = await levelcheck(ctx, playerins)   
    except:
        await ctx.send("Error! `,adminexp @ user (amount of exp)`")   
         
        
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
    gears = data.chooseobj("gear") 
    ul = data.chooseobj('update')  

@client.command()
async def givegear(ctx, member : discord.member, area, geartype, gearname):
    gearins = gears[area][geartype][gearname]
    playerins = players[str(member.id)]
    await addstuff(playerins, [gearins])
    embed = discord.Embed(title = f"Gave {gearins.name} to {member.name}")
    await ctx.send(embed=embed)

@atexit.register
def saveexit():
    fm.save(data)
    
client.run(TOKEN)
