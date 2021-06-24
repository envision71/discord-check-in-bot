import asyncio
from tempfile import TemporaryFile
from discord import channel, member
from discord.ext import commands
import discord
import os
import datetime
from discord.guild import Guild

from discord.role import Role
from quickstart import sheet
from discord.ext.commands.errors import MissingRole
from discord.raw_models import RawReactionActionEvent

conver = commands.converter
bot = commands.Bot(command_prefix='!')
CLIENT = discord.Client()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_NAME= os.getenv('DISCORD_SERVER_NAME')
CHANNEL = os.getenv('LISTEN_TO_CHANNEL')
ROLE = os.getenv('ROLE_TO_GIVE')
POST_CHANNEL = os.getenv('POST_TO_CHANNEL')
SHEET_ID = os.getenv('SHEET_ID')
SHEET_NAME = os.getenv('SHEET_NAME')
SEARCH_COLUMN = os.getenv('COLUMN_TO_SEARCH_THROUGH')
UPDATE_COLUMN = os.getenv('COLUMN_TO_UPDATE')
TEAM_NAME_COLUMN = os.getenv('TEAM_NAME_COLUMN')
TRACKID = []
sheet_interface = sheet(SHEET_ID,SHEET_NAME,SEARCH_COLUMN,UPDATE_COLUMN,TEAM_NAME_COLUMN)



async def channel_check(ctx):
   channel = await conver.TextChannelConverter().convert(ctx,CHANNEL)
   return channel == ctx.channel

@bot.command(name='check')
@commands.has_role('Admin')
async def test(ctx, check_in_time=1,sheet_id=SHEET_ID,*,tournament_name="Asguard 5v5"):
   print(ctx.channel)
   sheet_interface.SAMPLE_SPREADSHEET_ID=sheet_id
   await ctx.message.delete()
   d1 = str(datetime.datetime.now().date())
   msg = await ctx.send(("@everyone Check ins open for {0} {1} \n"+\
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
            await payload.member.edit(nick = ("["+team_name+"] "+payload.member.name))
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


