import asyncio
from discord import channel, member
from discord import guild
from discord import role
from discord.ext import commands
import discord
from discord_slash import SlashCommand, SlashCommandOptionType, SlashContext
import os
import datetime
from discord.guild import Guild
from discord.role import Role
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils import manage_commands
from discord_slash.utils.manage_commands import create_option, create_permission
from quickstart import sheet
from discord.ext.commands.errors import MissingRole
from discord.raw_models import RawReactionActionEvent
from dotenv import load_dotenv
load_dotenv()


open_flag = False
r1 = None
conver = commands.converter
bot = commands.Bot(command_prefix='!')
slash = SlashCommand(bot, sync_commands=True)
CLIENT = discord.Client()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_NAME= os.getenv('DISCORD_SERVER_NAME')
CHANNEL = os.getenv('LISTEN_TO_CHANNEL')
ROLE = os.getenv('ROLE_TO_GIVE')
POST_CHANNEL = os.getenv('POST_TO_CHANNEL')
SHEET_ID = os.getenv('SHEET_ID')
SHEET_NAME = os.getenv('SHEET_NAME')
SEARCH_COLUMN = os.getenv('TEAM_CAPTAIN_COLUMN_NAME')
UPDATE_COLUMN = os.getenv('CHECK_IN_COLUMN_NAME')
TEAM_NAME_COLUMN = os.getenv('TEAM_NAME_COLUMN_NAME')
ROLE_TO_PING = None
ROLER=None
TRACKID = []
sheet_interface = sheet(SHEET_ID,SHEET_NAME,SEARCH_COLUMN,UPDATE_COLUMN,TEAM_NAME_COLUMN)
options = [
            manage_commands.create_option(name = "role",description = "Role to assign",
                                          option_type = 8, required = "false"),
            manage_commands.create_option(name = "duration",description = "Minutes to leave check in open for.",
                                          option_type = 4, required = "false"),
            manage_commands.create_option(name = "sheet_id",description = "Google sheets ID to search for check-ins.",
                                          option_type = 3, required = "false"),
            manage_commands.create_option(name = "tournament_name",description = "Name of tournament",
                                          option_type = 3, required = "false"),
            manage_commands.create_option(name = "role_to_ping",description = "Role to ping",
                                          option_type = 8, required = "false")
]
options2 = [
            manage_commands.create_option(name = "roler",description = "Role to assign",
                                          option_type = 8, required = "false")
]
def nick_shortener(team_name,discord_name):
   nick = "["+team_name+"] "+discord_name
   if(len(nick)>32):
      nick = nick[:32]
   
   return nick


@slash.slash(name= 'start_check', description="Start check-ins for a tournament", options=options)
async def start_check(ctx:SlashContext,duration=1,sheet_id=SHEET_ID,tournament_name="Finchmas",role=ROLE,role_to_ping=ROLE_TO_PING):
   global r1
   global open_flag
   sheet_interface.SAMPLE_SPREADSHEET_ID=sheet_id
   d1 = str(datetime.datetime.now().date())
   open_flag = True
   if role_to_ping != None:
      msg = await ctx.send(("<@&{0}> Check ins open for {1} \n"+\
                           "Check ins close in {2} minutes from this message\n"+\
                           "Use /check to check-in").format(role_to_ping.id,tournament_name,duration),allowed_mentions=discord.AllowedMentions(roles=True))
   elif role_to_ping == None:
      msg = await ctx.send(("Check ins open for {0} \n"+\
                           "Check ins close in {1} minutes from this message\n"+\
                           "Use /check to check-in").format(tournament_name,duration)) 
   await asyncio.sleep(duration*60)
   msg = await ctx.send("{0} {1} check ins closed".format(d1,tournament_name))
   open_flag = False


@slash.slash(name="test",description="This is just a test command, nothing more.",options=options2)
async def test(ctx:SlashContext,roler=ROLER):
   print(roler.mentionable)
   await ctx.send(content="Hello World! <@&{0}>".format(roler.id),allowed_mentions=discord.AllowedMentions(roles=True))


@slash.slash(name = 'check', description="Check in for a tournament")
async def check(ctx:SlashContext):
   global r1
   if type(r1) == discord.role.Role:
      pass
   if not type(r1) == discord.role.Role:
      r1 = discord.utils.get(ctx.guild.roles,name=ROLE)
   global open_flag
   mashed = ctx.author.name +'#' +  ctx.author.discriminator
   mention_ID = '<@{}>'.format(ctx.author_id)
   if(open_flag): 
      row = sheet_interface.search(mashed,SEARCH_COLUMN)
      if not row == None:
         sheet_interface.add_checkmark(row)
         await ctx.author.add_roles(r1)
         team_name = sheet_interface.get_team_name(row)
         try:
            #print (team_name, ctx.author.name)
            await ctx.author.edit(nick=str(nick_shortener(team_name,ctx.author.name)))
         except:
            print(nick_shortener(team_name,ctx.author.name))
         msg = await ctx.send("{} has checked in".format(mention_ID))
      else:
         msg = await ctx.send("{} you are not a listed captain".format(mention_ID))
         return
   if(not open_flag):
     msg = await ctx.send("{} Check-ins are not open".format(mention_ID))
     return
     


@bot.event
async def on_command_error(ctx,error):
   if isinstance(error, MissingRole):
      await ctx.send(error)
   if isinstance(error, commands.CheckFailure):
      pass
   else:
      await ctx.send(error)

bot.run(TOKEN)


