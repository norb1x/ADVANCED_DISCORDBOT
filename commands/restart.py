import os
import sys
from discord.ext import commands

@commands.command()
async def restart(ctx):
    """
    Restartuje proces bota.
    Dostępne tylko dla administratorów serwera.
    """
    if ctx.author.guild_permissions.administrator:
        await ctx.send("Restartuję bota...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await ctx.send("Nie masz uprawnień do restartowania bota.")
