import asyncio
import shutil
import ffmpeg
import os
from discord.utils import get
from discord.ext import commands, timers
import discord
import datetime
import time
import random

TOKEN = 'ODI0OTM0MTI3MDg5NzQ1OTgw.YF2lxg.U7eIGkqJ6RFT3EmCV_8IuZ6iY4s'

bot = commands.Bot(command_prefix='#', description='Bot Of Our Discord Server')
bot.timer_manager = timers.TimerManager(bot)
spammer_fathers = list()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Lets Kill Them All!'))
    print(f'{bot.user.name} has connected to Discord!')
    # for guild in bot.guilds:
    #     print(f'{guild.name}(id: {guild.id})')


# AUTO  send welcome message to peopl
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        'Я смотрю ты вообще не понимаешь в каком месте ты оказался?\n'
        'Это сервер смерти\n'
        'Где тебе могут всадить пулю за считанные секунды\n'
        'И ты будешь сидеть на небесах и рыдать покамись твой труп лутает родион.\n'
        'Если ты хочешь знать как прожить хотя бы пять минут на сервере смерти - прослушай аудио')
    await member.dm_channel.send(file=discord.File("source\\sounds\\welcome.mp3"))


# send welcome message to people
@bot.command(aliases=['w'])
async def welcome(ctx, member: discord.Member):
    await member.create_dm()
    await member.dm_channel.send(
        'Я смотрю ты вообще не понимаешь в каком месте ты оказался?\n'
        'Это сервер смерти\n'
        'Где тебе могут всадить пулю за считанные секунды\n'
        'И ты будешь сидеть на небесах и рыдать покамись твой труп лутает родион.\n'
        'Если ты хочешь знать как прожить хотя бы пять минут на сервере смерти - прослушай аудио')
    await member.dm_channel.send(file=discord.File("source\\sounds\\welcome.mp3"))


# test command
@bot.command(aliases=["t"])
async def test(ctx):
    await ctx.send(f'All Good <@{ctx.author.id}>')


# kill the user
@bot.command()
async def kill(ctx, victim: discord.Member):
    # connect bot to user
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send('Bruh, you are not connected to voice chat!')
        return

    # play sound and test if we already in channel
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect(reconnect=False)
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
    vc.play(discord.FFmpegPCMAudio(executable="source\\ffmpeg\\bin\\ffmpeg.exe",
                                   source="source\\sounds\\headshot.mp3"))
    await asyncio.sleep(1)

    # disconnect user
    victim_member = discord.utils.get(ctx.guild.members, name=victim.name)
    await victim_member.move_to(None)

    # disconnect bot
    await vc.disconnect()


# make the bot join in vc
@bot.command()
async def join(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send('Bruh, you are not connected to voice chat!')
        return

    voice_channel = ctx.author.voice.channel
    await voice_channel.connect(reconnect=False)


# command who send dm_message to victim
@bot.command()
async def echo(ctx, victim: discord.Member, *message):
    await victim.send(f'{ctx.author.name}: {" ".join(message)}')


# command to start spam
@bot.command(aliases=['sp'])
async def start_spam(ctx, victim_id, time, name_time):
    global spammer_fathers
    spammer_fathers.append(ctx.author.id)
    spammer_fathers.append(int(victim_id[3:-1]))
    if name_time == 'sec':
        date = datetime.time(second=int(time))
    elif name_time == 'hours':
        date = datetime.time(hour=int(time))
    else:
        date = datetime.time(minute=int(time))
    date_next = datetime.datetime.combine(datetime.date.min, date) - datetime.datetime.min
    bot.timer_manager.create_timer('reminder', date_next,
                                   args=(ctx.channel.id, victim_id,
                                         '<@' + str(ctx.author.id) + '>',
                                         date_next))
    await ctx.send(f'The spammer should start at {time} {name_time}')


@bot.event
async def on_reminder(channel_id, victim_id, author_id, date_next):
    channel = bot.get_channel(channel_id)
    await channel.send(f'Wake up {victim_id}, we have a city to burn.')
    bot.timer_manager.create_timer('reminder', date_next,
                                   args=(channel_id, victim_id, author_id, date_next))


# command to stop spam
@bot.command()
async def stop_spam(ctx, *key):
    if ctx.author.id in spammer_fathers:
        bot.timer_manager.cancel()
        bot.timer_manager.clear()
        spammer_fathers.clear()
        await ctx.send('Spam machine stopped!')
    else:
        await ctx.send('Spam can only be stopped by the creator!')


@bot.command(aliases=['rus_roll'])
async def russian_roullete(ctx, time, name_time):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send('Bruh, you are not connected to voice chat!')
        return

    voice_channel = ctx.author.voice.channel
    if name_time == 'sec':
        date = datetime.time(second=int(time))
    elif name_time == 'hours':
        date = datetime.time(hour=int(time))
    else:
        date = datetime.time(minute=int(time))

    date_next = datetime.datetime.combine(datetime.date.min, date) - datetime.datetime.min
    bot.timer_manager.create_timer('roulette', date_next, args=(ctx, voice_channel,
                                                                ctx.channel.id,
                                                                date_next))
    await ctx.send(f'The russian roulete should start at {time} {name_time}')


@bot.event
async def on_roulette(ctx, voice_channel, channel_id, date_next):
    bot.timer_manager.create_timer('roulette', date_next, args=(ctx, voice_channel,
                                                                channel_id,
                                                                date_next))
    try:
        rand_n = random.randint(0, len(voice_channel.members) - 1)
        victim = voice_channel.members[rand_n]
        await victim.move_to(None)
    except Exception as e:
        pass


@bot.command(aliases=['roll_stop'])
async def stop_roll(ctx):
    bot.timer_manager.cancel()
    bot.timer_manager.clear()
    await ctx.send(
        f"Russian Roulette Stopped! I hope you don't have 1 more hole {str(bot.get_emoji(759722014700339210))}")


bot.run(TOKEN)
