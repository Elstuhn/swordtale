import discord
import time
import pickle
import asyncio
import random
from FileMonster import *
from discord.ext import commands
fm = FileMonster()
#setup begin
with open('token', 'rb') as readfile:
    TOKEN = pickle.load(readfile)


discord.Client(activity = discord.Game(name = ",help"))
##client = discord.Client(activity = discord.Game(name=",help"))
client = commands.Bot(command_prefix = ",")

class Player():
    def __init__(self, username, race):
        self.user = username
        self.race = race
        self.guild = None
        self.stats = {'dmg': 10, '


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

async def invite(message):
    yeet = client.get_guild(message.guild.id)
    embedVar = discord.Embed(title = "Invite the bot!")
    embedVar.add_field(name = "Invite Link", value = invite_link, inline=False)
    await message.channel.send(embed=embedVar)

@commands.has_permissions(manage_messages=True)
async def delete(message, num):
    await message.channel.purge(limit = int(num)+1)

async def server(message):
    yeet = client.get_guild(message.guild.id)
    embedVar = discord.Embed(title = f"{message.guild.name}")
    embedVar.add_field(name = "Total Members", value = yeet.member_count, inline=False)
    await message.channel.send(embed=embedVar)

async def help(message):
    embedVar = discord.Embed(title = "General Commands List")
    embedVar.add_field(name = ",help", value = "Shows this lol", inline=False)
    embedVar.add_field(name = ",invite", value = "Gets the invite link of the bot", inline=False)
    embedVar.add_field(name = ",server", value = "Gets information on the server", inline = False)
    embedVar.add_field(name = ",purge (messages)", value = "Purges an amount of messages", inline = False)
    embedVar.add_field(name = ",gamehelp", value = "Shows the help menu for game commands", inline=False)
    await message.channel.send(embed = embedVar)


async def timer():
    await client.wait_until_ready()

##@client.event
##async def on_member_update(before, after):
##    n = after.nick
##    if n:
##        if "elstuhn" in n.lower() or "elston" in n.lower():
##            last = before.nick
##
##            if last:
##                await after.edit(nick = last)
##            else:
##                await after.edit(nick = "nope")

@client.event
async def on_guild_join(guild):
    print(f"{client.user} has joined a new group!\nGroup Name: {guild.name}")


@client.event
async def on_message(message):
    if any([
        message.author == client.user,
        str(message.author.id) in banned,
        not prefix in message.content
        ]):
        return

    if message.content == ",invite":
        await invite(message)

    elif message.content == ",server":
        await server(message)

##    elif ",purge" in message.content:
##        contents = message.content.split()
##        if any([
##            not ",purge" in contents[0]
##            ]):
##            return
##        elif any([
##            len(contents) !=2,
##            not contents[1].isdigit()
##            ]):
##            await message.channel.send("Invalid Argument | ,purge (number of messages)")
##        elif any([
##            int(contents[1]) <1,
##            int(contents[1])>125
##            ]):
##            await message.channel.send("Error | Messages purged can only be lesser than 125 and more 0")
##        else:
##            await delete(message, contents[1])
    elif message.content == ",help":
        await help(message)

@client.command()
async def purge(ctx):
    await ctx.channel.purge(limit = 2)
                          

client.run(TOKEN)

#https://discord.com/api/oauth2/authorize?client_id=744156360094253107&permissions=8&redirect_uri=https%3A%2F%2Fwww.youtube.com%2FElstuhn&response_type=code&scope=identify%20connections%20guilds%20rpc%20messages.read%20webhook.incoming%20bot%20relationships.read

