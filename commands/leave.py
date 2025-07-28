from discord.ext import commands

@commands.command()
async def leave(ctx):
    """
    Komenda rozłączająca bota z kanału głosowego.
    """
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Bot opuścił kanał głosowy.")
    else:
        await ctx.send("Bot nie jest aktualnie połączony z żadnym kanałem głosowym.")
