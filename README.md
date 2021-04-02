# About
>You are summoned into Anomopheric, a world full of lore, secrets and adventures. Form guilds, parties, friendships and bonds to conquer Anomopheric and be the best amongst all. Explore and find out new information, hidden secrets and un-found mechanisms. As an adventurer, you are thrown into the game with little to no knowledge of it at all, providing immersive exploration, information-gathering and adventuring gameplay to the adventurers. Sub-classes, forging, crafting, exploration, slaying, friendships, large interactive environments and many more.

# ![The Discord (Invite Only)](https://discord.gg/2UyF3Yhh5g)

## Classes
**Player Class**
```class Player():
    def __init__(self, username, race):
        self.user = username
        self.race = race
        self.inventory = {}
        self.gear = {"weapon" : None, "secondary" : None, "helmet" : None, "chest" : None, "legs" : None, "boots" : None, "ring" : None, "amulet" : None, "special" : None}
        self.gold = 0
        self.level = 0
        self.exp = 0
        self.guild = None
        self.guildpos = None
        self.guildins = None
        self.party = None    #party instance
        self.statsp = {'hp' : 0, 'agility' : 0, 'looting' : 0,  'atk': 0, 'defense' : 0, 'phys_atk' : 0, 'phys_def' : 0, 'mag_def' : 0, 'mag_atk' : 0, 'cooldown_speed' : 0}
        self.stats = {'maxhp' : 20, 'hp' : 20, 'agility' : 0, 'atk': 5, 'defense' : 2, 'phys_atk' : 0, 'phys_def' : 0, 'mag_def' : 0, 'mag_atk' : 0}
        self.class_ = None
        self.skills = {"e" : [0, 0, 'Beginner', 'punch', 1, 1, 1, {}, 5]} #index 0: times used, index 1: level, index 2: level name, index 3: attack name, index 4: attack multiplier, 5: phy_atk multiplier, 6: mag_atk multiplier 7: {'buffname' : [seconds, {'buffs'('statname': percentage)}]} 8: cooldown time(seconds)
        self.location = ["4-4", "Agelock Town - It seems like time slows down in this town?"]
		self.fightstat = [None, 1] #In fight (if not, None, else, True) index 1 shows if dead or not (1 = alive, 0 = ded)
        self.status = "Adventurer"
		self.advcard = None```
 
**Adventurer's Guild Class**
```class Adventurers_Guild():
    def __init__(self, questlist):
		self.questlist = questlist
		self.members = {}
		
	def register(self, playerins):
		card = Adventurers_Card(playerins.user)
		playerins.advcard = card
		self.members[str(playerins.author.id)] = card```
    
**Party Class**
```class Party():
    def __init__(self, owner):
        self.owner = owner
        self.members = [owner] #list will be full of player id in str
		
	def checkdead(self):
		out = True #if out is false at the end, not all dead
		for i in self.members:
			playerins = players[i]
			if playerins.stats['hp'] >= 1:
				out = False
		return out```
    
**Role Class**
```class Role():
    def __init__(self, name, position, kickPerms = False, invitePerms = False, setrolePerms = False, rolecreationPerms = False, editPerms = False):
        self.name = name
        self.kickPerms = kickPerms
        self.invitePerms = invitePerms
        self.setrolePerms = setrolePerms
        self.rolecreationPerms = rolecreationPerms
        self.editPerms = editPerms
        self.pos = position```
        
**Guild Class**
```class Guild():
    def __init__(self, name : str, owner : str):
        self.name = name
        self.owner = owner # ctx.author.id in str form
        self.value = data.chooseobj('players')[f'{owner}'].gold #set initial guild value to owner's gold amount
        self.members = {} #memberid : membername
        self.roles = {'Guild Master' : guildmaster, 'Member' : member}
        self.rolepos = ['Guild Master', 0, 0, 0, 0, 0, 'Member']```
        
**Mob Class**
```class Mob():
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
        self.multiplier = multiplier```
        
**Aventurer's Card Class**
```class Adventurers_Card():
	def __init__(self, user):
		self.owner = user
		self.rank = "F"
		self.quests = {}
		self.questcount = 0
		self.title = None
	
	def check_rank(self, rank):
		return self.rank == rank
	
	def updaterank(self):
		#check if requirements fulfilled```
    
    
  
