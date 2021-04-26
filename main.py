import asyncio
import datetime
import json
import logging
import random
import sqlite3
import sys
import traceback

import discord
import requests
import vk_api
import wikipediaapi
from discord.ext import commands, timers
from discord.ext.commands import has_any_role
from youtube_dl import YoutubeDL

# dialogs, messages and reactions data
with open('dialogs.json', encoding='utf-8') as data_file:
    data = json.load(data_file)

    dialogs = data['dialogs']
    img_meetings = data['img_meetings']
    reactions = data['reactions']
    id_groups_for_mems = data['id_groups_for_mems']
    permission_roles = data['permission_roles']
    who_can_ban = data['who_can_ban']
    who_can_kick = data['who_can_kick']
    TOKEN = data['TOKEN']
    login, password = data['LOGIN'], data['PASSWORD']
    bots_game = data['bot_play_game']
    prefix = data['prefix']

bot = commands.Bot(command_prefix=prefix, description='Bot Of Our Discord Server')
bot.timer_manager = timers.TimerManager(bot)
spammer_fathers = list()

# logging
with open('discord.log', encoding='utf-8', mode='a') as file:
    file.write(
        '-----------------------------------New Session-----------------------------------\n')
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))
logger.addHandler(handler)

# messages to delete
bin_messages_id = []

# vars used play music
songs = list()


@bot.event
async def on_ready():
    if bots_game:
        await bot.change_presence(activity=discord.Game(name=bots_game))
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
    embed = discord.Embed(title=f'All Good!',
                          colour=discord.Colour.orange())
    await ctx.send(embed=embed)
    logger.debug('Command to test def sended')
    logger.warning('Command to test def sended')


# kill the user
@bot.command(description='This command will connect to your voice channel and kick @user.\n'
                         'Example: #kill @user')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def kill(ctx, victim: discord.Member):
    # connect bot to user
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        embed = discord.Embed(title=dialogs['error_connect'],
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)
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


@bot.command(deescription='This command calls AMOGUS')
@commands.has_any_role(permission_roles['Master'])
async def amogus(ctx):
    # connect bot to user
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        embed = discord.Embed(title="Amogus doesn't understand where to go!",
                              colour=discord.Colour.orange())
        await ctx.send(embed=embed)
        return

    # play sound and test if we already in channel
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect(reconnect=False)
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
    vc.play(discord.FFmpegPCMAudio(executable="source\\ffmpeg\\bin\\ffmpeg.exe",
                                   source="source\\sounds\\amogus.mp3"))
    await asyncio.sleep(2)

    # disconnect user
    members = voice_channel.members
    for member in members:
        await member.move_to(None)

    # disconnect bot
    await vc.disconnect()

    logger.info(f'<@{ctx.author.id}> calls AMOGUS!1!3qw!f7eds')


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
    embed = discord.Embed(title="Message sended!",
                          colour=discord.Colour.green())
    await ctx.send(embed=embed)
    logger.info(f'Echo message sended to: {victim.display_name}, from: <@{ctx.author.id}>')


# command to start spam
@bot.command(aliases=['sp'],
             description='This command will start spam mashine. \n '
                         'Example: #start_spam @user 5 min')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def start_spam(ctx, victim_id, time=10, name_time='sec'):
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
    embed = discord.Embed(title=f'The spammer should start at {time} {name_time}!',
                          colour=discord.Colour.green())
    await ctx.send(embed=embed)
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
        embed = discord.Embed(title="Spam machine stopped!",
                              colour=discord.Colour.green())
        await ctx.send(embed=embed)
        for message in bin_messages_id:
            try:
                await message.delete()
            except Exception as e:
                pass
        logger.info(f'Spammer stopped by: <@{ctx.author.id}>')
    else:
        embed = discord.Embed(title="Spam can be stopped only be the creator!",
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)
        logger.info(f'Trying to stop spammer by: <@{ctx.author.id}>')


@bot.command(aliases=['rus_roll'],
             description='Starts playing Russian roulette. \nExample: #rus_roll 5 min')
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
    embed = discord.Embed(title=f'The russian roulette should start at {time} {name_time} ✅',
                          colour=discord.Colour.green())
    await ctx.send(embed=embed)
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
    embed = discord.Embed(title="Russian Roulette Stopped!",
                          description=f"I hope you don't"
                                      f" have 1 more hole "
                                      f"{str(bot.get_emoji(759722014700339210))}",
                          colour=discord.Colour.green())
    await ctx.send(embed=embed)
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
    embed = discord.Embed(title="The meeting is successfully set!",
                          colour=discord.Colour.green())
    await ctx.send(embed=embed)

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
    embed = discord.Embed(title="All time cleaned!",
                          colour=discord.Colour.green())
    await ctx.send(embed=embed)
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
    embed = discord.Embed(title="Report sended, thanks for help!",
                          colour=discord.Colour.green())
    await ctx.send(embed=embed)
    logger.warning(f'Bug reported by: <@{ctx.author.id}>')


@bot.command(aliases=['cb', 'start_cyberbooling', 'cyberbooling'],
             description='This command start cyberbooling')
@commands.has_any_role(permission_roles['Master'])
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


# @bot.command(aliases=['rec'], description='Command start record speak')
# @commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
# async def record(ctx):  # TODO
#     voice_channel = ctx.author.voice.channel
#     if ctx.voice_client is None:
#         vc = await voice_channel.connect(reconnect=False)
#     else:
#         await ctx.voice_client.move_to(voice_channel)
#         vc = ctx.voice_client
#     audiosource = discord.AudioSource().read()
#     print(audiosource)


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
    vc.play(discord.FFmpegPCMAudio(executable="source\\ffmpeg\\bin\\ffmpeg.exe", source=URL,
                                   **FFMPEG_OPTIONS))
    logger.info(f'Music started by: <@{ctx.author.id}>, music: {url}')


@bot.command(description='Command stopped music')
@commands.has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    embed = discord.Embed(title="Music stopped!",
                          colour=discord.Colour.green())
    await ctx.send(embed=embed)
    await voice_client.disconnect()
    logger.info(f'Music stopped by: <@{ctx.author.id}>')


@bot.command(description='Kick user and send funny audio')
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
        embed = discord.Embed(title="Error", description=f"You can't kick users!",
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)


@bot.command(description='Ban user and send funny video')
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
        embed = discord.Embed(title="Error", description=f"You can't ban users!",
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)


@bot.command(aliases=['bomb', 'bm'], description='Message has been deleted after N time')
@has_any_role(permission_roles['Master'], permission_roles['Commander'])
async def bomb_message(ctx, time: int, name_time, *message):
    if name_time == 'sec':
        delete_on_time = time
    elif name_time == 'hours' or name_time == 'hrs':
        delete_on_time = time * 60 * 60
    else:
        delete_on_time = time * 60
    try:
        await ctx.message.add_reaction('✅')  # add react
        await asyncio.sleep(delete_on_time)  # spim)
        await ctx.message.delete()  # delete message after spim
    except Exception as e:
        pass


@bot.command(description='Returns random cat image')
async def cat(ctx, n=1):
    if 1 <= n <= 10:
        for _ in range(n):
            response = requests.get('https://api.thecatapi.com/v1/images/search').json()[0]
            await ctx.send(str(response['url']))
        logger.info(f'Get cat from: {ctx.author.id}')
    else:
        embed = discord.Embed(title="Error", description=f"Неверное количество! 1 <= n <= 10",
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)


@bot.command(description='Returns random dog image')
async def dog(ctx, n=1):
    if 1 <= n <= 10:
        for _ in range(n):
            response = requests.get('https://dog.ceo/api/breeds/image/random').json()
            await ctx.send(str(response['message']))
        logger.info(f'Get dog from: {ctx.author.id}')
    else:
        embed = discord.Embed(title="Error", description=f"Неверное количество! 1 <= n <= 10",
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)


@bot.command(aliases=['memas', 'mems'],
             description='Returns random Mememememememememmememme')
async def mem(ctx, n=1):
    vk_session = vk_api.VkApi(
        login, password)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
    vk = vk_session.get_api()
    if 1 <= n <= 10:
        for _ in range(n):
            response = vk.photos.get(owner_id=-int(random.choice(id_groups_for_mems)),
                                     album_id='wall',
                                     offset=random.randint(0, 1000),
                                     count=1)
            await ctx.send(response['items'][0]['sizes'][-1]['url'])
        logger.info(f'Get mem from: {ctx.author.id}')
    else:
        embed = discord.Embed(title="Error", description=f"Неверное количество! 1 <= n <= 10",
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)


@bot.command(description='Returns information about theme')
async def wiki(ctx, *text):
    text = ' '.join(text)
    wiki_wiki = wikipediaapi.Wikipedia('ru')
    page = wiki_wiki.page(text)
    if page.exists():
        embed = discord.Embed(title=text, description=page.summary[0:150] + '...',
                              colour=discord.Colour.dark_green())
        embed.add_field(name="url: ", value=page.fullurl, inline=False)
        await ctx.send(embed=embed)
        logger.info(f'Wikipedia page founded, url: {page.fullurl}, from: {ctx.author.id}')
    else:
        embed = discord.Embed(title='Информация не найдена!', colour=discord.Colour.red())
        await ctx.send(embed=embed)
        logger.info(f'Wikipedia page not found! Text: {text}')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            embed = discord.Embed(title="I could not find that member! Please try again. ❌",
                                  colour=discord.Colour.red())
            await ctx.send(embed=embed)
            logger.error(f'Member not found from: <@{ctx.author.id}>')
        else:
            embed = discord.Embed(title="Bad argument, please try again!",
                                  colour=discord.Colour.red())
            await ctx.send(embed=embed)
            logger.error(f'Bad argument error from: <@{ctx.author.id}>')

    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="I could not find this command, please check the spelling! ❌",
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)
        logger.error(f'Command not found from: <@{ctx.author.id}>')

    elif isinstance(error, commands.MissingAnyRole):
        embed = discord.Embed(title="Access is denied ⛔",
                              colour=discord.Colour.red())
        await ctx.send(embed=embed)
        logger.error(f'Access is denied from: <@{ctx.author.id}>')
    elif isinstance(error, commands.CommandInvokeError):
        print(error)
    else:
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def main():
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
