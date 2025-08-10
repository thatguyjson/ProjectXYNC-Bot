'''
Project: XYNC Bot is a discord bot created using the Nextcord API Wrapper.
This was created by Jason, also known as @Json or @drip___ on discord!
For any questions, feel free to add and dm me on discord "drip___"
'''
import nextcord
import mysql.connector
import asyncio
import time
import random
import requests
import json
import re
import pytz
import os
from nextcord.ext import commands, tasks
from nextcord.ui import View, Select
from datetime import datetime, timedelta, timezone
from constants import *
from emojis import *

"""
these intents allow the bot to track member activity, read messages, monitor reactions,
receive server-level events, and listen to messages in guilds. All these are necessary for bot functionality
like moderation, command handling, and reacting to user input.
"""
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.guild_messages = True
intents.messages = True

'''
commands.bot(command_prefix='', intents=intents), we are setting the prefix
that commands will run in discord itself. intents=intents is telling the bot
to use the intents we previously set to True above so that we can use it and
make the bot more versatile.
'''
bot = commands.Bot(command_prefix='?', intents=intents)


# This might be used somewhere maybe...
msg_ids = {}

# DB Connection below grabs all DB info related stuff in order to connect from Constants(Available in PebbleHost)
db = mysql.connector.connect(
    host=DBhost,
    user=DBuser,
    password=DBpassword,
    database=DBdatabase,
    port=DBport
)

"""
down below is on_ready + bot.run
"""
@bot.event
async def on_ready():
    global welcomeChannel
    log_channel = bot.get_channel(1402518002552803378)
    welcomeChannel = bot.get_channel(1402518002552803378)
    if welcomeChannel is None:
        await log_channel.send("Could not find the welcome channel.")
    else:
        await log_channel.send(f'Logged in as {bot.user.name}. I am ready to go <@639904427624628224>!')

'''

SEPARATING EVERYHITNG THAT RUNS AFTER BOT TURNS ON

'''
emoji_role_map = {
    fortniteEmoji: 1402512807701774428,
    tftEmoji: 1403233017568432269,
    lolEmoji: 1402512736629428254,
    csgoEmoji: 1402512792011014165,
    valorantEmoji: 1402512751162822706,
    marvelrivalsEmoji: 1403255089556226099,
    minecraftEmoji: 1402512775745507409,
    maleEmoji: 1402513160149139456,
    femaleEmoji: 1402513175835967528,
    othergenderEmoji: 1402513187827613758,
    hehimEmoji: 1402513079266443334,
    sheherEmoji: 1402513119401742440,
    theythemEmoji: 1402513137940566126,
    simsEmoji: 1403820574853173258,
}
gameMessage = 1403614984122142791
genderMessage = 1403615112769699921
pronounsMessage = 1403615268567257099
reaction_role_messages = {gameMessage, genderMessage, pronounsMessage}


@bot.event
async def on_raw_reaction_add(payload: nextcord.RawReactionActionEvent):
    log_channel = bot.get_channel(1402518002552803378)
    if payload.message_id not in reaction_role_messages:
        return
    emoji_str = str(payload.emoji)
    role_id = emoji_role_map.get(emoji_str)
    if role_id:
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return
        role = guild.get_role(role_id)
        member = await guild.fetch_member(payload.user_id)
        if role and member:
            await member.add_roles(role, reason="Reaction role added")
            await log_channel.send(f"Gave **{role.name}** to **{member.name}**")

@bot.event
async def on_raw_reaction_remove(payload: nextcord.RawReactionActionEvent): 
    log_channel = bot.get_channel(1402518002552803378)
    if payload.message_id not in reaction_role_messages:
        return
    emoji_str = str(payload.emoji)
    role_id = emoji_role_map.get(emoji_str)
    if role_id:
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return
        role = guild.get_role(role_id)
        member = await guild.fetch_member(payload.user_id)
        if role and member:
            await member.remove_roles(role, reason="Reaction role removed")
            await log_channel.send(f"Removed **{role.name}** from **{member.name}**")

@bot.command()
async def announce(ctx, channel: nextcord.TextChannel = None, mention_type: str = None, *, message: str = None):
    # Safety net: No arguments provided
    if channel is None or message is None:
        usage = (
            "**Usage:** `!announce #channel [mention_type] message`\n"
            "**Example 1:** `!announce #general everyone Server maintenance tonight`\n"
            "**Example 2:** `!announce #updates here New patch just dropped!`\n"
            "**Example 3:** `!announce #news none Just a regular announcement.`\n\n"
            "`mention_type` must be one of: `everyone`, `here`, or `none`."
        )
        await ctx.send(usage)
        return

    mention = ""
    if mention_type:
        mention_type = mention_type.lower()
        if mention_type == "everyone":
            mention = "@everyone"
        elif mention_type == "here":
            mention = "@here"
        elif mention_type != "none":
            await ctx.send("❌ Invalid mention type. Use `everyone`, `here`, or `none`.")
            return
    try:
        await channel.send(f"{mention} {message}".strip())
        await ctx.send(f"✅ Announcement sent in {channel.mention}")
    except Exception as e:
        await ctx.send(f"❌ Failed to send message: {e}")


bot.run(botToken)
