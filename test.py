async def on_ready(self):
    print(f'{self.user} has connected to Discord!')
    for guild in self.guilds:
        print(f'{guild.name}(id: {guild.id})')


async def on_member_join(self, member):
    print("New Member!")
    await member.create_dm()
    await member.dm_channel.send(file=discord.File("/source/sounds/welcome.mp3"))
----------------------------------------------------------------------
    # voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    # channel = discord.utils.get(ctx.bot.get_all_channels(), guild__name='Cool', name='general')
    # print(voice_client.disconnect())

    # await ctx.guild.ban(user, reason="Testing", delete_message_days=0)

----------------------------------------------------------------------
# # disconnect user
#     victim_member = discord.utils.get(ctx.guild.members, name=victim.name)
#     kick_channel = await ctx.guild.create_voice_channel("kick")
#     try:
#         await victim_member.move_to(None)
#     except Exception as e:
#         pass
#     await kick_channel.delete()

----------------------------------------------------------------------
# @bot.command()
# async def kill(ctx, victim: discord.Member):
#     # connect bot to user
#     if ctx.author.voice is None or ctx.author.voice.channel is None:
#         await ctx.send('Bruh, you are not connected to voice chat!')
#         return
#
#     # play sound and test if we already in channel
#     voice_channel = ctx.author.voice.channel
#     if ctx.voice_client is None:
#         vc = await voice_channel.connect(reconnect=False)
#     else:
#         await ctx.voice_client.move_to(voice_channel)
#         vc = ctx.voice_client
#     vc.play(discord.FFmpegPCMAudio(executable="source\\ffmpeg\\bin\\ffmpeg.exe",
#                                    source="source\\sounds\\headshot.mp3"))
#     await asyncio.sleep(1)
#
#     # disconnect user
#     victim_member = discord.utils.get(ctx.guild.members, name=victim.name)
#     await victim_member.move_to(None)
#
#     # disconnect bot
#     await vc.disconnect()
# ---------------------------------------------------------------------------
# dialogs = {'welcome': 'Я смотрю ты вообще не понимаешь в каком месте ты оказался?\n'
#                       'Это блять сервер смерти\n'
#                       'Где тебе могут всадить пулю за считанные секунды\n'
#                       'И ты будешь сидеть на небесах и рыдать как сучка покамись твой труп лутает родион.\n'
#                       'Если ты хочешь знать как прожить хотя бы пять минут на сервере смерти - прослушай аудио',
#            'wake up': 'Wake the fuck up {}, we have a city to burn. ⚠️',
#            'error_connect': 'Bruh, you are not connected to voice chat!',
#            'error_command_mistake': 'I think you made a mistake. \nCheck #help <command> to get more information.❌'}



# @bot.event
# async def on_message(message):
#     if 'глеб' in message.content.lower() or 'tess' in message.content.lower():
#         emojis = ['🇳🇮🇨🇪🇬🇺🇾', '🆒🚹']
#         emo = random.choice(emojis)
#         for emoji in emo:
#             await message.add_reaction(emoji)



# async def access_test(ctx):
#     if "bot master" not in [role.name.lower() for role in ctx.author.roles]:
#         await ctx.send(f'Access is denied ⛔')
#         return False
#     return True