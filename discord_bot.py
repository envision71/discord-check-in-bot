import asyncio
from discord import channel, member
from discord import guild
from discord import role
from discord.ext import commands
import discord
import discord_slash
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
                                          option_type = 3, required = "false")
]
options2 = [
            manage_commands.create_option(name = "role",description = "Role to assign",
                                          option_type = 8, required = "false")
]
def nick_shortener(team_name,discord_name):
   nick = "["+team_name+"] "+discord_name
   if(len(nick)>32):
      nick = nick[:32]
   
   return nick


#@slash.permission(guild_id=894433155770114119,permissions=[create_permission(894435570103746620, SlashCommandPermissionType.ROLE, True)])
@slash.slash(name= 'start_check', description="Start check-ins for a tournament", options=options)
async def start_check(ctx:SlashContext,duration=1,sheet_id=SHEET_ID,tournament_name="Finchmas",role=ROLE):
   global r1
   global open_flag
   r1 = role
   sheet_interface.SAMPLE_SPREADSHEET_ID=sheet_id
   d1 = str(datetime.datetime.now().date())
   open_flag = True
   msg = await ctx.send(("@everyone Check ins open for {0} \n"+\
                        "Check ins close in {1} minutes from this message\n"+\
                        "Use /check to check-in").format(tournament_name,duration))
   await asyncio.sleep(duration*60)
   msg = await ctx.send("{0} {1} check ins closed".format(d1,tournament_name))
   open_flag = False

@slash.slash(name="test",
             description="This is just a test command, nothing more.")
async def test(ctx):
  await ctx.send(content="Hello World!")
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
     

async def channel_check(ctx):
   channel = await conver.TextChannelConverter().convert(ctx,CHANNEL)
   return channel == ctx.channel

@bot.command(name='check')
async def test(ctx, check_in_time=1,sheet_id=SHEET_ID,*,tournament_name="Finchmas"):
   sheet_interface.SAMPLE_SPREADSHEET_ID=sheet_id
   await ctx.message.delete()
   d1 = str(datetime.datetime.now().date())
   msg = await ctx.send((" Check ins open for {0} {1} \n"+\
                        "Check ins close in {2} minutes from this message\n"+\
                        "React with ✅ to check in").format(d1,tournament_name,check_in_time))
   await msg.add_reaction("✅")
   TRACKID.append(msg.id)
   await asyncio.sleep(check_in_time*60)
   await msg.delete()
   msg = await ctx.send("{0} {1} check ins closed".format(d1,tournament_name))

   
async def add(payload):
   if payload.message_id in TRACKID:
      discord_ID = payload.member.name +'#' + payload.member.discriminator
      mention_ID = '<@{}>'.format(payload.user_id)
      row = sheet_interface.search(discord_ID)
      if not row == None:
         sheet_interface.add_checkmark(row)
         await payload.member.add_roles(discord.utils.get(payload.member.guild.roles,name=ROLE))
         team_name = sheet_interface.get_team_name(row)
         try:
            await payload.member.edit(nick_shortener(team_name,+payload.member.name))
         except:
            pass
         channel = await bot.fetch_channel(payload.channel_id)
         msg = await channel.send("{} has checked in".format(mention_ID))

         
async def remove(payload):
   if payload.message_id in TRACKID:
      discord_ID = await bot.fetch_user(payload.user_id)
      row = sheet_interface.search(str(discord_ID))
      if not row == None:
         sheet_interface.remove_checkmark(row)
         guild = await bot.fetch_guild(payload.guild_id)
         member_id = await guild.fetch_member(payload.user_id)
         await member_id.remove_roles(discord.utils.get(guild.roles,name=ROLE))
         try:
            await member_id.edit(nick = (member_id.name))
         except:
            pass
         channel = await bot.fetch_channel(payload.channel_id)
         tag = '<@{}>'.format(payload.user_id)
         msg = await channel.send('{} has un-check in'.format(tag))
bot.add_listener(add, 'on_raw_reaction_add')
bot.add_listener(remove, 'on_raw_reaction_remove')


@bot.event
async def on_command_error(ctx,error):
   if isinstance(error, MissingRole):
      await ctx.send(error)
   if isinstance(error, commands.CheckFailure):
      pass
   else:
      await ctx.send(error)

bot.run(TOKEN)


