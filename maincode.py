import discord
import time
import typing as t
from time import sleep
import os
import pickle
import asyncio
import random
from discord.ext import commands
from datetime import datetime
from collections import defaultdict

fileopened = {}


class FileMonster(defaultdict):
    
    def __init__(self, *args, **kwargs):
        super().__init__(list, *args, **kwargs)
        
    def create(self):
        return Storage()

    def save(self, storage):
        for i in fileopened:
            if fileopened[i] == hex(id(storage)):
                with open(i+".fm", "wb") as file:
                    pickle.dump(storage, file)
                return
        raise SystemError("Storage was not found.")

    def createsave(self, storage, filename : str, ask : bool = True):
        if ask:
            try:
                open(filename+".fm", "r")
                open(filename+".fm", "r").close()
                _ = input("It looks like you have a file with the same name. Would you like to overwrite it? (Y/N)\n")
            
                while _.lower() not in ["y", "n"]:
                    _ = input("It looks like you have a file with the same name. Would you like to overwrite it? (Y/N)\n")

                if _.lower() == "n":
                    print("Operation cancelled.")
                    return
                
            except:
                pass
        
        with open(filename+".fm", 'wb') as file:
            pickle.dump(storage, file)
            
        if ask:
            print("Saved file in", filename+".fm") 

    def load(self, filename : str):
        
        try:
            open(filename+".fm", "r")
            open(filename+".fm", "r").close()

        except:
            raise SystemError(f"Filename '{filename}' does not exist.")
        
        with open(filename+".fm", 'rb') as read:
            pickled = pickle.load(read)
            fileopened[filename] = hex(id(pickled))
            return pickled

    def showfiles(self):
        print("List of files:")
        files = [f for f in os.listdir() if all([os.path.isfile(f), ".fm" in f])]
        if not len(files):
            print("No FileMonster files found.")
        for i in files:
            print(i)

    def merge(self, *storages):
        if len(storages) == 1 or not len(storages):
            raise SystemError("Need 2 or more Storage objects to merge")
        newstorage = storages[0]
        #keys = list(newstorage.storage.keys())
        for i in storages[1:]:
            if not isinstance(i, Storage):
                raise SystemError("Arguments must all be Storage objects")
            
            #keysadd = list(i.storage.keys())
            #for labels in keys:
                #if labels in keysadd:
                    #mergedict(newstorage, i)
                    
            #newstorage.storage.update(i.storage)

            for k, v in i.storage.items():
                newstorage.storage[k].extend(v)
            
        return newstorage
            
class SystemError(Exception):
    pass

class Storage():
    def __init__(self):
        self.storage = {}

    def __str__(self):
        return "<Storage Object at "+hex(id(self))+">"

    def __repr__(self):
        return self.storage
        
    def bulkadd(self, *objects):
        for i in objects:
            print(i)
            label = input("\nPlease enter the label you want for this object.\n")

            try:
                self.storage[label].append(i)
                        
            except:
                self.storage[label] = [i]

    def add(self, label : str, object_ : t.Any):

        try:
            self.storage[label].append(object_)
        except:
            self.storage[label] = [object_]
        
        return


    def remove_label(self, label : str):
        try:
            self.storage[label]
        except:
            raise SystemError(f"{label} was not found in data storage unit")

        del self.storage[label]

    def remove_elem(self, label : str, pos : int = 0):
        try:
            self.storage[label]
        except:
            raise SystemError(f"Label {label} was not found.")

        try:
            self.storage[label][pos]
        except:
            raise SystemError("Position is out of range.")

        del self.storage[label][pos]

    def bulkremove(self, *labels):
        if not len(labels):
            raise SystemError(f"Missing arguments.")
        
        invalid = 0
        valid = 0 
        for i in labels:
            
            try:
                self.storage[i]
                valid += 1
            except:
                invalid += 1
                continue
            
            del self.storage[i]

        if invalid:
            print(f"{invalid} invalid labels were detected.")
        print(f"{valid} valid labels and their corresponding data has been deleted.")

    def clear(self):
        self.storage = {}

    def showlabels(self):
        labels = []
        print("Labels:")
        for keys in self.storage:
            print(keys)
            labels.append(keys)
        return labels

    def showstorage(self):
        print(self.storage)

    def getstorage(self):
        return self.storage
    
    def chooseobj(self, label : str, pos : int = 0):
        try:
            self.storage[label]
        except:
            raise SystemError(f"Label {label} was not found.")

        try:
            self.storage[label][pos]
        except:
            raise SystemError("Position is out of range.")

        
        return self.storage[label][pos]

    def prettyshow(self):
        count = 1
        for i in self.storage:
            print(f"\nLabel {count} : {i}")
            sleep(0.5)
            print("Content:")
            sleep(1.2)
            for z in self.storage[i]:
                print(z)
            count += 1
            sleep(1.7)


fm = FileMonster()
data = fm.load("data")
banned = data.chooseobj("banned")
races = data.chooseobj("races")
admin = data.chooseobj("admins")
players = data.chooseobj("players")
playerlist = list(players)
skills = data.chooseobj("skills")
levels = data.chooseobj("levels")

#setup begin
with open('token', 'rb') as readfile:
    TOKEN = pickle.load(readfile)

intents = discord.Intents.all()

##client = discord.Client(activity = discord.Game(name=",help"))
client = commands.Bot(command_prefix = ",", activity = discord.Game(name=",help"), intents=intents, help_command = None)

class Guild():
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.value = data.chooseobj('players')[f'{owner}'].gold #set initial guild value to owner's gold amount
        self.members = []

    async def promote(ctx, member : discord.Member):
        
        

async def checkstart(ctx, game = False, private = False):
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
    else:
        return True
    
class Player():
    def __init__(self, username, race):
        self.user = username
        self.race = race
        self.inventory = {}
        self.gear = []
        self.gold = 0
        self.level = 0
        self.exp = 0
        self.guild = None
        self.guildpos = None
        self.guildins = None
        self.statsp = {'hp' : 0, 'agility' : 0, 'looting' : 0,  'atk': 0, 'defense' : 0, 'phys_atk' : 0, 'phys_def' : 0, 'mag_def' : 0, 'mag_atk' : 0, 'cooldown_speed' : 0}
        self.stats = {'hp' : 20, 'agility' : 0, 'atk': 5, 'defense' : 2, 'phys_atk' : 0, 'phys_def' : 0, 'mag_def' : 0, 'mag_atk' : 0}
        self.class_ = None
        self.skills = {"punch" : [0, 0, 'Beginner', 'e']} #index 0: times used, index 1: level, index 2: level name, index 3: keybind


@client.event
async def on_ready():
    servers = 0
    print("Connected servers:")
    for guild in client.guilds:
        print(guild.name, guild.id)
        servers+=1
    print(f"\n\n{client.user} has connected to Discord on {servers} servers.")

invite_link = "https://discord.com/api/oauth2/authorize?client_id=744156360094253107&permissions=8&scope=bot"

prefix = ","

#Setup finished
#functions begin

async def timer():
    await client.wait_until_ready()

async def calcstats(playerinst):
    pass
    

@client.event
async def on_guild_join(guild):
    print(f"{client.user} has joined a new group!\nGroup Name: {guild.name}")


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
    if not perms:
        await ctx.send("You need the manage messages permission!")
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
    embed = discord.Embed(title = "Game Commands", colour = discord.Colour(1520))
    embed.add_field(name = ",start", value = "starts your adventure", inline= False)
    embed.add_field(name = ",player", value = "shows your player info", inline= False)
    embed.add_field(name = ",stats", value = "shows your stats", inline = False)
    embed.add_field(name = ",create_guild (guild name)", value = "creates a guild (needs 4k gold)", inline = False)
    await ctx.send(embed = embed)

@client.command()
async def start(ctx):
    check = await checkstart(ctx, private = True)
    if not check:
        return
    def checknum(message):
        return message.author == ctx.author

    if str(ctx.author.id) in players:
        await ctx.send("You already have a save! Are you sure you want to create a new save? [y/n]")
        try:
            _ = await client.wait_for("message", check=checknum, timeout = 10)
            _ = _.content
            if _ != "y":
                await ctx.send("Cancelled.")
                return
        except asyncio.TimeoutError as e:
            await ctx.send("You took too long")
            return

            
    await ctx.send("You can do this tutorial in DMs, it might be better, continue? (y/n)")
    try:
        _ = await client.wait_for("message", check= checknum, timeout = 10)
        _ = _.content
        if _ != "y":
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
        number = await client.wait_for("message", check=checknum, timeout = 20)
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
        playername = playername.content
        if not playername.isalnum():
            await ctx.send("Player name has to be alphanumerical.")
            return
        elif len(playername) < 3:
            await ctx.send("Length of name has to be more than 2.")
            return
        
    except asyncio.TimeoutError as e:
        await ctx.send("You took too long!")
        return
    playerins = Player(playername, playerrace)
    players[f'{ctx.author.id}'] = playerins
    await ctx.send("Player registered.")
    embed = discord.Embed()
    embed.add_field(name = "__**Elston**__", value = f"Welcome to Sword Tale {playername}! Your only current skill is 'punch', use it enough and who knows what will happen? You can explore the world of Anomopheric to\
 kill monsters to gain loot and exp to get more powerful, do dungeons/raids to get dungeon/raid loot, discover new things, items, mechanics, skills. Large interactive map and exploration available to you in Sword Tale!")
    embed.set_thumbnail(url = "https://m.media-amazon.com/images/I/51Q30qp+LEL._AC_SX355_.jpg")
    await ctx.send(embed = embed)
    embed = discord.Embed(title = "Be the first person or guild to raid and complete dungeons! There are much to be discovered and much that are hidden. Hopefully you find them all ;)")
    embed.add_field(name = "\u200b", value = "-From yours truly, Elston")
    await ctx.send(embed = embed)
    racestat = races[playerrace]
    for stat in racestat:
        playerins.statsp[stat] += racestat[stat]
    

@client.command(aliases = ["playerinfo"])
async def player(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerstat = players[str(ctx.author.id)] #gets player instance of sender
    embed = discord.Embed(title = f"**__{playerstat.user}'s Info__**")
    embed.add_field(name = "Gold :coin:", value = f"{playerstat.gold}")
    embed.add_field(name = "Race :flag_white:", value = f"{playerstat.race}", inline = True)
    embed.add_field(name = "Level :arrow_up:", value = f"{playerstat.level} [{playerstat.exp}/{levels[playerstat.level]}]", inline = True)
    embed.add_field(name = "Guild :beginner:", value = f"{playerstat.guild}", inline = True)
    embed.add_field(name = "Guild Position :military_helmet:", value = f"{playerstat.guildpos}", inline=True)
    embed.add_field(name = "\u200b", value = "\u200b", inline=False)
    _ = '\n'.join(list(playerstat.skills))
    embed.add_field(name = "Skills :bulb:", value = f"{_}")
    _ = []
    for i in playerstat.skills:
        _.append(f"{playerstat.skills[i][3]}")
    _ = '\n'.join(_)
    embed.add_field(name = "Keybind :keyboard:", value = f"{_}")
    _ = []
    for i in playerstat.skills:
        _.append(f"{playerstat.skills[i][2]}")
    _ = '\n'.join(_)
    embed.add_field(name = "Skill Level :low_brightness:", value = f"{_}")
    await ctx.send(embed= embed)

@client.command(aliases = ["stat"])
async def stats(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    player = players[str(ctx.author.id)]
    playerstats = player.statsp
    embed = discord.Embed(title = f"**__{player.user}'s Stats__**")
    embed.add_field(name = "\u200b", value = "\u200b")
    embed.add_field(name = "**__Percentages__**", value = "\u200b")
    embed.add_field(name = "\u200b", value = "\u200b")
    embed.add_field(name = "HP :heart:", value = f"{playerstats['hp']}%")
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
    embed.add_field(name = "HP :heart:", value = f"{playerstats['hp']}")
    embed.add_field(name = "Agility :dash:", value = f"{playerstats['agility']}")
    embed.add_field(name = "Attack :dagger:", value = f"{playerstats['atk']}")
    embed.add_field(name = "Defense :shield:", value = f"{playerstats['defense']}")
    embed.add_field(name = "Physical Attack", value = f"{playerstats['phys_atk']}")
    embed.add_field(name = "Physical Defense", value = f"{playerstats['phys_def']}")
    embed.add_field(name = "Magic Attack", value = f"{playerstats['mag_atk']}")
    embed.add_field(name = "Magic Defense", value = f"{playerstats['mag_def']}")
    await ctx.send(embed=embed)

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
    elif playerins.gold < 4000:
        await ctx.send("Not enough gold!")
        return
    
    playerins.gold -= 4000
    guildins = Guild(guildname, f'{ctx.author.id}')
    playerins.guildpos = "Leader"
    playerins.guild = guildname
    playerins.guildins = guildins
    await ctx.send(f"Guild '{guildname}' has been created by {ctx.author.name}!")

@client.command(aliases = ["gpromote"])
async def guildpromote(ctx, member : discord.Member):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f"{ctx.author.id}"]
    playerins2 = players[f"{member.id}"]
    if playerins.guildpos != "Leader":
        await ctx.send("You must be the Leader of the guild to do this!")
        return
    elif playerins2.guild != playerins.guild:
        await ctx.send("Player must be part of your guild!")
        return
    elif playerins2.guildpos not in ["Member", "Officer"]

@client.command(aliases = ["guildinfo"])
async def guild(ctx):
    check = await checkstart(ctx, game = True)
    if not check:
        return

@client.command()
async def ginvite(ctx, member : discord.Member):
    check = await checkstart(ctx, game = True)
    if not check:
        return
    playerins = players[f'{ctx.author.id}']
    guild = playerins.guildins
    if guild.owner != ctx.
    
    
@client.command()
async def admingold(ctx, member : discord.Member, gold : int):
    if str(ctx.author.id) not in admin:
        await ctx.send("Sorry! You do not have permission.")
        return
    try:
        playerins = players[f'{member.id}']
        playerins.gold += gold
        await ctx.send(f"Gave {gold} gold to {member.name}")
    except:
        await ctx.send("Error! `,admingold @ user (amount of gold)`")
        
@client.command()
async def adminsave(ctx):
    if str(ctx.author.id) not in admin:
        await ctx.send("Sorry! You do not have permission.")
        return
    fm.save(data)
    await ctx.send("Saved!")
     
client.run(TOKEN)
