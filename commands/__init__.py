from discord.ext import commands
# commands/__init__.py

class Pepper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_pepper.start()  
