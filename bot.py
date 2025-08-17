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

DISCORD_CHANNEL_ID = 1402540266757558273

@tasks.loop(seconds=30)
async def question_of_the_day():
    log_channel = bot.get_channel(1402518002552803378)
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    pst_tz = pytz.timezone('America/Los_Angeles')
    now_pst = now_utc.astimezone(pst_tz)
    if now_pst.hour == 6 and now_pst.minute == 0:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions WHERE is_used = 0 ORDER BY RAND() LIMIT 1;")
        question_row = cursor.fetchone()
        if question_row:
            question_text = question_row['question']
            channel = bot.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                await channel.send(f"📌 **Question of the Day:**\n{question_text}")
                update_query = "UPDATE questions SET is_used = 1 WHERE question = %s;"
                cursor.execute(update_query, (question_text,))
                db.commit()
        cursor.close()

    else:
        await log_channel.send('testing loops for now')
        
    

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
        await log_channel.send(f'Starting QOTD loop.')
        await question_of_the_day.start()
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
ownerId = 639904427624628224


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
            "**Usage:** `?announce #channel [mention_type] message`\n"
            "**Example 1:** `?announce #general everyone Server maintenance tonight`\n"
            "**Example 2:** `?announce #updates here New patch just dropped!`\n"
            "**Example 3:** `?announce #news none Just a regular announcement.`\n\n"
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

@bot.command()
async def giveaway(ctx, duration: str = None, *, prize: str = None):
    log_channel = bot.get_channel(1402518002552803378)
    if duration is None or prize is None:
        await ctx.send(
            "❌ Usage: `!giveaway <duration> <prize>`\n"
            "Examples:\n`!giveaway 1d Nitro Giveaway!`\n`!giveaway 4h Steam Gift Card!`\n`!giveaway 30m Free Role!`"
        )
        return
    unit = duration[-1]
    if not duration[:-1].isdigit() or unit not in ["d", "h", "m"]:
        await ctx.send("❌ Invalid format. Use a number followed by `d`, `h`, or `m` (e.g., 1d, 3h, 45m).")
        return
    time_value = int(duration[:-1])
    if unit == "d":
        total_seconds = time_value * 86400
    elif unit == "h":
        total_seconds = time_value * 3600
    elif unit == "m":
        total_seconds = time_value * 60

    embed = nextcord.Embed(
        title="🎉 Giveaway!",
        description=(
            f"**Prize:** {prize}\n"
            "React with 🎉 to enter!\n"
            f"React with {cancelgiveawayEmoji} to cancel the giveaway (Json Only Feature).\n"
            f"Hosted by: {ctx.author.mention} ends @ {nextcord.utils.format_dt(nextcord.utils.utcnow() + timedelta(seconds=total_seconds))}"
        ),
        color=nextcord.Color.green()
    )
    giveaway_msg = await ctx.send(embed=embed)
    await ctx.message.delete()
    await giveaway_msg.add_reaction("🎉")
    emoji_obj = nextcord.utils.get(ctx.guild.emojis, id=1403999126835695687)
    if emoji_obj:
        await giveaway_msg.add_reaction(emoji_obj)
    else:
        await giveaway_msg.add_reaction(cancelgiveawayEmoji)
    def check(reaction, user):
        return (
            reaction.message.id == giveaway_msg.id and
            str(reaction.emoji) in ["🎉", cancelgiveawayEmoji] and
            user != bot.user
        )
    giveaway_ended = False
    try:
        while not giveaway_ended:
            reaction, user = await bot.wait_for("reaction_add", timeout=total_seconds, check=check)

            if str(reaction.emoji) == cancelgiveawayEmoji:
                if user.id == ownerId:
                    await ctx.send(f"❌ {prize} Giveaway cancelled by {user.mention}. Now deleting original giveaway message.")
                    await giveaway_msg.delete()
                    giveaway_ended = True
                    break
                else:
                    bewareMsg = ctx.send(f"❌ {user.mention}, you are not authorized to cancel this giveaway. Json has been alerted, please dont do this again.")
                    await log_channel.send(f'<@{ownerId}> FYI, {user.mention} is trying to canceled the giveaway.')
                    time.sleep(3)
                    await bewareMsg.delete()
    except asyncio.TimeoutError:
        giveaway_ended = True

    if giveaway_ended and str(reaction.emoji) == cancelgiveawayEmoji:
        return
    fetched_msg = await ctx.channel.fetch_message(giveaway_msg.id)
    reaction = nextcord.utils.get(fetched_msg.reactions, emoji="🎉")
    if not reaction:
        await ctx.send("❌ No entries received.")
        return
    users = await reaction.users().flatten()
    users = [user for user in users if not user.bot]
    if not users:
        await ctx.send("❌ No valid (non-bot) entries.")
        return
    winner = random.choice(users)
    await ctx.send(f"🎉 Congrats {winner.mention}! You won **{prize}**!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted {len(deleted)-1} messages.", delete_after=5)

bot.run(botToken)
