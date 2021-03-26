import asyncio
from discord.ext import commands
import discord

TOKEN = 'ODI0OTM0MTI3MDg5NzQ1OTgw.YF2lxg.U7eIGkqJ6RFT3EmCV_8IuZ6iY4s'


class DiscordBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(file=discord.File("/source/sounds/welcome.mp3"))


def main():
    print('main')
    bot = commands.Bot(command_prefix='!')
    bot.add_cog(DiscordBot(bot))
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
