import asyncio
import shutil
import ffmpeg
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
import os
from discord.ext import commands, timers
from discord.ext.commands import has_permissions, has_any_role, has_guild_permissions
import discord
import datetime
import time
import random
import traceback
import sys
import sqlite3
import logging

TOKEN = 'ODI0OTM0MTI3MDg5NzQ1OTgw.YF2lxg.O3YbqQ8_wT4JDzhsnjLUYP5iptA'

bot = commands.Bot(command_prefix='#', description='Bot Of Our Discord Server')
bot.timer_manager = timers.TimerManager(bot)
spammer_fathers = list()

# vars used play music
songs = list()

# permissions
who_can_ban = [430677550600028161, 532157271531061255]
who_can_kick = [430677550600028161, 532157271531061255]
permission_roles = {'Master': 'Bot Master',
                    'Commander': 'Bot Commander'}
# dialogs and messages
dialogs = {'welcome': 'Я смотрю ты вообще не понимаешь в каком месте ты оказался?\n'
                      'Это блять сервер смерти\n'
                      'Где тебе могут всадить пулю за считанные секунды\n'
                      'И ты будешь сидеть на небесах и рыдать как сучка покамись твой труп лутает родион.\n'
                      'Если ты хочешь знать как прожить хотя бы пять минут на сервере смерти - прослушай аудио',
           'wake up': 'Wake the fuck up {}, we have a city to burn. ⚠️',
           'error_connect': 'Bruh, you are not connected to voice chat!',
           'error_command_mistake': 'I think you made a mistake. \nCheck #help <command> to get more information.❌'}

# reactions
reactions = {'Good': ':white_check_mark:',
             'Bad': ':no_entry:'}

# img for meetings messages
img_meetings = ['meet1.jpg', 'meet2.jpg', 'meet3.png']

# messages to delete
bin_messages_id = []

# logging
with open('discord.log', encoding='utf-8', mode='a') as file:
    file.write(
        '-----------------------------------New Session-----------------------------------\n')
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))
logger.addHandler(handler)


# async def access_test(ctx):
#     if "bot master" not in [role.name.lower() for role in ctx.author.roles]:
#         await ctx.send(f'Access is denied ⛔')
#         return False
#     return True


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Lets Kill Them All!'))
    print(f'{bot.user.name} has connected to Discord!')
    logger.info('Bot ready to use!')
    # for guild in bot.guilds:
    #     print(f'{guild.name}(id: {guild.id})')


# AUTO  send welcome message to peopl
@bot.event
async def on_member_join(member: discord.Member):
    await member.create_dm()
    await member.dm_channel.send(dialogs['welcome'])
    await member.dm_channel.send(file=discord.File("source\\sounds\\welcome.mp3"))
    logger.info(f'New member: {member.display_name}')


@bot.event
async def on_message(message: discord.Message):
    if 'глеб' in message.content.lower():
        emojis = ['🇳🇮🇨🇪🇬🇺🇾', '🆒🚹']
        emojis = random.choice(emojis)
        for emoji in emojis:
            await message.add_reaction(emoji)


# send welcome message to people
@bot.command(aliases=['w'],
             description='This command will send welcome '
                         'message to @user.\n Example: #welcome @user')
async def welcome(ctx, member: discord.Member):
    await member.create_dm()
    await member.dm_channel.send(dialogs['welcome'])
    await member.dm_channel.send(file=discord.File("source\\sounds\\welcome.mp3"))
    await ctx.send('Welcome sended! ✅')
    logger.info(
        f'Welcome message sended to: {member.display_name}, from: <@{ctx.author.id}>')


# test command
@bot.command(aliases=["t"])
async def test(ctx):
    await ctx.send(f'All Good <@{ctx.author.id}>')
    logger.debug('Command to test def sended')
    logger.warning('Command to test def sended')


# kill the user
@bot.command(description='This command will connect to your voice channel and kick @user.\n'
                         'Example: #kill @user')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def kill(ctx, victim: discord.Member):
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

    logger.info(f'<@{ctx.author.id}> killed {victim.display_name}')


# make the bot join in vc
@bot.command(description='This command will connect bot to your voice channel')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def join(ctx):
    voice_channel = ctx.author.voice.channel
    await voice_channel.connect(reconnect=False)
    logger.info(f'Joined to voice channel. Command from: <@{ctx.author.id}>')


# command who send dm_message to victim
@bot.command(
    description='This command will send message to @user from Bot.\n '
                'Example: #echo @user Hi boomer')
@commands.has_any_role(permission_roles['Master'])
async def echo(ctx, victim: discord.Member, *message):
    # send message
    await victim.send(f'{ctx.author.name}: {" ".join(message)}')
    await ctx.send('Message sended! ✅')
    logger.info(f'Echo message sended to: {victim.display_name}, from: <@{ctx.author.id}>')


# command to start spam
@bot.command(aliases=['sp'],
             description='This command will start spam mashine. \n '
                         'Example: #start_spam @user 5 min')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def start_spam(ctx, victim_id, time, name_time):
    # spam
    global spammer_fathers
    spammer_fathers.append(ctx.author.id)
    spammer_fathers.append(int(victim_id[3:-1]))
    if name_time == 'sec':
        if int(time) >= 5:
            date = datetime.time(second=int(time))
        else:
            await ctx.send(f'Minimal interval - 5 sec!')
            return
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
    logger.info(f'Starting spam to id:{str(victim_id)}, from: <@{ctx.author.id}>')


@bot.event
async def on_reminder(channel_id, victim_id, author_id, date_next):
    channel = bot.get_channel(channel_id)
    message = await channel.send(dialogs['wake up'].format(victim_id))
    bot.timer_manager.create_timer('reminder', date_next,
                                   args=(channel_id, victim_id, author_id, date_next))
    bin_messages_id.append(message)
    logger.info(f'Spam to id: {str(victim_id)}')


# command to stop spam
@bot.command(
    description='This command will stop the spam machine. \n This can '
                'only be done by the creator of the machine or the one '
                'at whom it is directed.')
async def stop_spam(ctx, *key):
    if ctx.author.id in spammer_fathers or not spammer_fathers:
        bot.timer_manager.cancel()
        bot.timer_manager.clear()
        spammer_fathers.clear()
        await ctx.send('Spam machine stopped! ✅')
        for message in bin_messages_id:
            try:
                await message.delete()
            except Exception as e:
                pass
        logger.info(f'Spammer stopped by: <@{ctx.author.id}>')
    else:
        await ctx.send('Spam can only be stopped by the creator!')
        logger.info(f'Trying to stop spammer by: <@{ctx.author.id}>')


@bot.command(aliases=['rus_roll'],
             description='Starts playing Russian roulette. \nExample: #russ_roll 5 min')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def russian_roullete(ctx, time, name_time):
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
    await ctx.send(f'The russian roulette should start at {time} {name_time} ✅')
    logger.info(
        f'Russian roulette started time:{str(time)} {name_time}, from: <@{ctx.author.id}>')


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
    logger.info(f'Roullet shoot to: {victim.display_name}')


@bot.command(aliases=['roll_stop'],
             description='This command stops the Russian roulette game. Any user can stop it.')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
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
    logger.info(f'Russian Roulette stopped by: <@{ctx.author.id}>')


@bot.command(aliases=['new_meet', 'meeting'], description='This command will set meeting time')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def new_meeting(ctx, time: int, time_type, text, *users: discord.Member):
    if time_type == 'sec':
        date_next = time
    elif time_type == 'hours' or time_type == 'hrs':
        date_next = time * 60 * 60
    else:
        date_next = time * 60
    await ctx.send(f'The meeting is successfully set ✅')

    logger.info(f'Created new meeting users: {[user.display_name + " " for user in users]}; '
                f'from: <@{ctx.author.id}>; time: {str(time)} {time_type}')

    await asyncio.sleep(date_next)

    img = random.choice(img_meetings)

    for user in users:
        await user.create_dm()
        await user.dm_channel.send(f"The meeting about {text} is coming, don't miss it!",
                                   file=discord.File(f"source\\img\\{img}"))
    logger.info('Meeting end!')


@bot.command(description='This command delete all timers, roulets and meetings')
@commands.has_any_role(permission_roles['Master'])
async def clear_time(ctx):
    bot.timer_manager.cancel()
    bot.timer_manager.clear()
    await ctx.send('All time cleaned ✅')
    logger.info(f'Time cleared by: <@{ctx.author.id}>')


@bot.command(description='This command kick bot from voice channel')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def disconnect(ctx):
    try:
        vc = ctx.voice_client
        await vc.disconnect()
    except Exception as e:
        pass
    logger.info(f'Bot disconnected by: <@{ctx.author.id}>')


@bot.command(description='This command report bug and send to developer')
async def report_bug(ctx, *text):
    con = sqlite3.connect('reported.db')
    cur = con.cursor()
    cur.execute(
        f"""INSERT INTO Bugs 
        VALUES('{datetime.datetime.now().strftime("%d/%m/%Y")}','{str(ctx.author)}','{' '.join(text)}')""")
    con.commit()
    con.close()
    await ctx.send('Report sended, thanks for help!')
    logger.warning(f'Bug reported by: <@{ctx.author.id}>')


@bot.command(aliases=['cb', 'start_cyberbooling', 'cyberbooling'],
             description='This command start cyberbooling')
@commands.has_any_role(permission_roles['Master'])  # TODO
async def cyberbool(ctx, member: discord.Member, time, time_name, *reason):
    # go mute
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")
        # for channel in guild.channels:
        #     await channel.set_permissions(mutedRole, speak=False, send_messages=False,
        #                                   read_message_history=True, read_messages=True,
        #                                   listen=True, view_channel=True, connect=True,
        #                                   move_members=False)
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
    logger.info(f'Start cyberbooling to: {member.display_name}, from: <@{ctx.author.id}>')


@bot.command(aliases=['stop_cb', 'stop_cyberbool'], description='This command stop cyberbooling')
@commands.has_any_role(permission_roles['Master'])
async def stop_cyberbooling(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(mutedRole)
    await member.send(f"You have unmuted from: - {ctx.guild.name}")
    embed = discord.Embed(title="Stop Cyberbooling", description=f" unmuted-{member.mention}",
                          colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)
    await member.edit(mute=False)
    logger.info(f'Cyberbooling stopped by: <@{ctx.author.id}>, to: {member.display_name}')


@bot.command(aliases=['rec'], description='Command start record speak')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def record(ctx):  # TODO
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect(reconnect=False)
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
    # vc.listen(MySinc())


@bot.command(description='Command start youtube music')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def play(ctx, url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'False'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'}
    vc = await ctx.author.voice.channel.connect()
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']
    vc.play(
        FFmpegPCMAudio(executable="source\\ffmpeg\\bin\\ffmpeg.exe", source=URL,
                       **FFMPEG_OPTIONS))
    logger.info(f'Music started by: <@{ctx.author.id}>, music: {url}')


@bot.command(description='Command stopped music')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await ctx.send('Music stopped!')
    await voice_client.disconnect()
    logger.info(f'Music stopped by: <@{ctx.author.id}>')


@bot.command(description='Kick user and send funny audio')
@has_any_role(permission_roles['Master'])
async def kick(ctx, victim: discord.Member, reason="Couldn't survive on the server"):
    if ctx.author.id in who_can_kick:
        await victim.create_dm()
        await victim.dm_channel.send(file=discord.File("source\\sounds\\Crazy Frog.mp3"))
        await victim.dm_channel.send(f'Kick reason: {reason}')
        embed = discord.Embed(title="Kicked User", description=f"{victim.mention} was kicked!",
                              colour=discord.Colour.light_gray())
        embed.add_field(name="reason:", value=reason, inline=False)
        await ctx.send(embed=embed)
        await victim.kick(reason=reason)
        logger.info(f'<@{ctx.author.id}> kicked {victim.display_name}, reason: {reason}')
    else:
        await ctx.send(f"You can't kick users!")


@bot.command(description='Ban user and send funny video')
@commands.has_any_role(permission_roles['Master'])
async def ban(ctx, victim: discord.Member, reason="Couldn't survive on the server"):
    if ctx.author.id in who_can_ban:
        await victim.create_dm()
        await victim.dm_channel.send('https://www.youtube.com/watch?v=FXPKJUE86d0')
        await victim.dm_channel.send(f'Ban reason: {reason}')
        embed = discord.Embed(title="Banned User", description=f"{victim.mention} was banned!",
                              colour=discord.Colour.light_gray())
        embed.add_field(name="reason:", value=reason, inline=False)
        await ctx.send(embed=embed)
        await victim.ban()
        logger.info(f'<@{ctx.author.id}> banned {victim.display_name}, reason: {reason}')
    else:
        await ctx.send(f"You can't kick users!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            await ctx.send('I could not find that member! Please try again.❌')
            logger.error(f'Member not found from: <@{ctx.author.id}>')
        else:
            await ctx.send('Bad argument, please try again!')
            logger.error(f'Bad argument error from: <@{ctx.author.id}>')

    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('I could not find this command, please check the spelling!❌')
        logger.error(f'Command not found from: <@{ctx.author.id}>')

    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send(f'Access is denied ⛔')
        logger.error(f'Access is denied from: <@{ctx.author.id}>')
    elif isinstance(error, commands.CommandInvokeError):
        print(error)
    # elif isinstance(error, commands.MissingRequiredArgument):
    #     await ctx.send()
    else:
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@bot.command(description='Test Func')
async def t_f(ctx):  # TODO
    # await ctx.author.delete_message(ctx.message)
    print(ctx.message.content)
    print(ctx.message.id)
    await ctx.message.delete()


@bot.command(aliases=['bomb', 'bm'], description='Message has been deleted after N time')
async def bomb_message(ctx, time: int, name_time, *message):
    if name_time == 'sec':
        delete_on_time = time
    elif name_time == 'hours' or name_time == 'hrs':
        delete_on_time = time * 60 * 60
    else:
        delete_on_time = time * 60
    await ctx.message.add_reaction('✅')  # add react
    await asyncio.sleep(delete_on_time)  # spim)
    await ctx.message.delete()  # delete message after sleep


def main():
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
