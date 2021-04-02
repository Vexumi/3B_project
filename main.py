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
import traceback
import sys
import sqlite3

dialogs = {'welcome': 'Я смотрю ты вообще не понимаешь в каком месте ты оказался?\n'
                      'Это блять сервер смерти\n'
                      'Где тебе могут всадить пулю за считанные секунды\n'
                      'И ты будешь сидеть на небесах и рыдать как сучка покамись твой труп лутает родион.\n'
                      'Если ты хочешь знать как прожить хотя бы пять минут на сервере смерти - прослушай аудио',
           'wake up': 'Wake the fuck up {}, we have a city to burn. ⚠️',
           'error_connect': 'Bruh, you are not connected to voice chat!',
           'error_command_mistake': 'I think you made a mistake. \nCheck #help <command> to get more information.❌'}

TOKEN = 'ODI0OTM0MTI3MDg5NzQ1OTgw.YF2lxg.IBVoC8JQvjJYH4WR_FHjio1rB2w'

bot = commands.Bot(command_prefix='#', description='Bot Of Our Discord Server')
bot.timer_manager = timers.TimerManager(bot)
spammer_fathers = list()


async def access_test(ctx):
    if "bot master" not in [role.name.lower() for role in ctx.author.roles]:
        await ctx.send(f'Access is denied ⛔')
        return False
    return True


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
    await member.dm_channel.send(dialogs['welcome'])
    await member.dm_channel.send(file=discord.File("source\\sounds\\welcome.mp3"))


# send welcome message to people
@bot.command(aliases=['w'],
             description='This command will send welcome '
                         'message to @user.\n Example: #welcome @user')
async def welcome(ctx, member: discord.Member):
    await member.create_dm()
    await member.dm_channel.send(dialogs['welcome'])
    await member.dm_channel.send(file=discord.File("source\\sounds\\welcome.mp3"))
    await ctx.send('Welcome sended! ✅')


# test command
@bot.command(aliases=["t"])
async def test(ctx):
    await ctx.send(f'All Good <@{ctx.author.id}>')


# kill the user
@bot.command(description='This command will connect to your voice channel and kick @user.\n'
                         'Example: #kill @user')
async def kill(ctx, victim: discord.Member):
    # access test
    if not await access_test(ctx):
        return

    # connect bot to user
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send(dialogs['error_connect'])
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


@kill.error
async def error_kill(ctx, error):
    await ctx.send(dialogs['error_command_mistake'])


# make the bot join in vc
@bot.command(description='This command will connect bot to your voice channel')
async def join(ctx):
    if not await access_test(ctx):
        return

    voice_channel = ctx.author.voice.channel
    await voice_channel.connect(reconnect=False)


# command who send dm_message to victim
@bot.command(
    description='This command will send message to @user from Bot.\n '
                'Example: #echo @user Hi boomer')
async def echo(ctx, victim: discord.Member, *message):
    # access test
    if not await access_test(ctx):
        return
    # send message
    await victim.send(f'{ctx.author.name}: {" ".join(message)}')
    await ctx.send('Message sended! ✅')


@echo.error
async def error_echo(ctx, error):
    await ctx.send(dialogs['error_command_mistake'])


# command to start spam
@bot.command(aliases=['sp'],
             description='This command will start spam mashine. \n '
                         'Example: #start_spam @user 5 min')
async def start_spam(ctx, victim_id, time, name_time):
    # access test
    if not await access_test(ctx):
        return

    # spam
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
    await ctx.send(f'The spammer should start at {time} {name_time} ✅')


@start_spam.error
async def error_start_spam(ctx, error):
    await ctx.send(dialogs['error_command_mistake'])


@bot.event
async def on_reminder(channel_id, victim_id, author_id, date_next):
    channel = bot.get_channel(channel_id)
    await channel.send(dialogs['wake up'].format(victim_id))
    bot.timer_manager.create_timer('reminder', date_next,
                                   args=(channel_id, victim_id, author_id, date_next))


# command to stop spam
@bot.command(
    description='This command will stop the spam machine. \n This can '
                'only be done by the creator of the machine or the one '
                'at whom it is directed.')
async def stop_spam(ctx, *key):
    if ctx.author.id in spammer_fathers:
        bot.timer_manager.cancel()
        bot.timer_manager.clear()
        spammer_fathers.clear()
        await ctx.send('Spam machine stopped! ✅')
    else:
        await ctx.send('Spam can only be stopped by the creator!')


@bot.command(aliases=['rus_roll'],
             description='Starts playing Russian roulette. \nExample: #russ_roll 5 min')
async def russian_roullete(ctx, time, name_time):
    # access test
    if not await access_test(ctx):
        return
    # test if author in voice channel
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send(dialogs['error_connect'])
        return

    voice_channel = ctx.author.voice.channel
    if name_time == 'sec':
        date = datetime.time(second=int(time))
    elif name_time == 'hours' or name_time == 'h' or name_time == 'hrs':
        date = datetime.time(hour=int(time))
    else:
        date = datetime.time(minute=int(time))

    date_next = datetime.datetime.combine(datetime.date.min, date) - datetime.datetime.min
    bot.timer_manager.create_timer('roulette', date_next, args=(ctx, voice_channel,
                                                                ctx.channel.id,
                                                                date_next))
    await ctx.send(f'The russian roulete should start at {time} {name_time} ✅')


@russian_roullete.error
async def error_rus_roll(ctx, error):
    await ctx.send(dialogs['error_command_mistake'])


@bot.event
async def on_roulette(ctx, voice_channel, channel_id, date_next):
    bot.timer_manager.create_timer('roulette', date_next, args=(ctx, voice_channel,
                                                                channel_id,
                                                                date_next))
    # play sound
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect(reconnect=False)
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
    vc.play(discord.FFmpegPCMAudio(executable="source\\ffmpeg\\bin\\ffmpeg.exe",
                                   source="source\\sounds\\rus_roll_shot.mp3"))
    await asyncio.sleep(7.1)
    # kick user
    try:
        rand_n = random.randint(0, len(voice_channel.members) - 1)
        victim = voice_channel.members[rand_n]
        await victim.move_to(None)
    except Exception as e:
        pass


@bot.command(aliases=['roll_stop'],
             description='This command stops the Russian roulette game. Any user can stop it.')
async def stop_roll(ctx):
    bot.timer_manager.cancel()
    bot.timer_manager.clear()
    try:
        vc = ctx.voice_client
        await vc.disconnect()
    except Exception as e:
        pass
    await ctx.send(
        f"Russian Roulette Stopped! I hope you don't "
        f"have 1 more hole {str(bot.get_emoji(759722014700339210))}")


@bot.command(aliases=['new_meet'], description='This command will set meeting time')
async def new_meeting(ctx, time, time_type, *text, **users: discord.Member):
    if time_type == 'time':
        time = time.split('/')
        date = datetime.datetime(day=time[0], month=time[0], year=time[0])
    else:
        date = datetime.time(minute=int(time))

    date_next = datetime.datetime.combine(datetime.date.min, date) - datetime.datetime.min
    bot.timer_manager.create_timer('meet', date_next, args=(ctx, text, users))
    await ctx.send(f'The meeting is successfully set ✅')


@new_meeting.error
async def error_new_meeting(ctx, error):
    await ctx.send(dialogs['error_command_mistake'])


@bot.event
async def on_meet(ctx, text, users):
    for user in users:
        await user.create_dm()
        await user.dm_channel.send(f"The meeting about {text} is coming, don't miss it!")


@bot.command(description='This command delete all timers, roulets and meetings')
async def clear_time(ctx):
    if not await access_test(ctx):
        return
    bot.timer_manager.cancel()
    bot.timer_manager.clear()
    await ctx.send('All time cleaned ✅')


@bot.command(description='This command kick bot from voice channel')
async def disconnect(ctx):
    if not await access_test(ctx):  # access test
        return

    try:
        vc = ctx.voice_client
        await vc.disconnect()
    except Exception as e:
        pass


@bot.command(description='This command report bug and send to developer')
async def report_bug(ctx, *text):
    if not await access_test(ctx):  # access test
        return

    con = sqlite3.connect('reported.db')
    cur = con.cursor()
    cur.execute(
        f"""INSERT INTO Bugs 
        VALUES('{datetime.datetime.now().strftime("%d/%m/%Y")}','{str(ctx.author)}','{' '.join(text)}')""")
    con.commit()
    con.close()
    await ctx.send('Report sended, thanks for help!')


@report_bug.error
async def error_report_bug(ctx, error):
    await ctx.send(dialogs['error_command_mistake'])


@bot.command(aliases=['cb'], description='This command start cyberbooling')
async def cyberbool(ctx, member: discord.Member, time, time_name, *reason):
    if not await access_test(ctx):  # access test
        return

    # go mute
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False,
                                          read_message_history=False, read_messages=True,
                                          listen=True, view_channel=True, connect=True,
                                          move_members=False)
    embed = discord.Embed(title="Cyberbooling", description=f"{member.mention} was muted ",
                          colour=discord.Colour.light_gray())
    embed.add_field(name="reason:", value=' '.join(reason), inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=' '.join(reason))
    await member.send(
        f"You have been cyberbooled!\n From: {guild.name}\n Reason: {' '.join(reason)}")

    # time
    if time_name == 'hours' or time_name == 'hrs':
        time = int(float(time) * 60 * 60)
    else:
        time = int(time) * 60

    # unmute if time end
    await member.edit(mute=True)
    await asyncio.sleep(time)
    await member.edit(mute=False)
    await member.remove_roles(mutedRole)
    await member.send(f"You have unmuted from: - {ctx.guild.name}")
    embed = discord.Embed(title="Stop Cyberbooling", description=f" unmuted-{member.mention}",
                          colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)


@cyberbool.error
async def error_cyberbool(ctx, error):
    await ctx.send(dialogs['error_command_mistake'])


@bot.command(aliases=['stop_cb', 'stop_cyberbool'], description='This command stop cyberbooling')
async def stop_cyberbooling(ctx, member: discord.Member):
    if not await access_test(ctx):  # access test
        return

    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(mutedRole)
    await member.send(f"You have unmuted from: - {ctx.guild.name}")
    embed = discord.Embed(title="Stop Cyberbooling", description=f" unmuted-{member.mention}",
                          colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)
    await member.edit(mute=False)


@stop_cyberbooling.error
async def error_stop_cyberbooling(ctx, error):
    await ctx.send(dialogs['error_command_mistake'])


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            await ctx.send('I could not find that member! Please try again.❌')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('I could not find this command, please check the spelling!❌')
    else:
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


bot.run(TOKEN)
