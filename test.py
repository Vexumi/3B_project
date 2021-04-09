# async def on_ready(self):
#     print(f'{self.user} has connected to Discord!')
#     for guild in self.guilds:
#         print(f'{guild.name}(id: {guild.id})')
#
#
# async def on_member_join(self, member):
#     print("New Member!")
#     await member.create_dm()
#     await member.dm_channel.send(file=discord.File("/source/sounds/welcome.mp3"))
# ----------------------------------------------------------------------
    # voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    # channel = discord.utils.get(ctx.bot.get_all_channels(), guild__name='Cool', name='general')
    # print(voice_client.disconnect())

    # await ctx.guild.ban(user, reason="Testing", delete_message_days=0)

# ----------------------------------------------------------------------
# # disconnect user
#     victim_member = discord.utils.get(ctx.guild.members, name=victim.name)
#     kick_channel = await ctx.guild.create_voice_channel("kick")
#     try:
#         await victim_member.move_to(None)
#     except Exception as e:
#         pass
#     await kick_channel.delete()

# ----------------------------------------------------------------------
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
import logging

logging.basicConfig(filename='logs.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')



def log_to_file():
    i = 0
    while i < 10:
        logging.warning(i)
        i += 1


if __name__ == '__main__':
    log_to_file()