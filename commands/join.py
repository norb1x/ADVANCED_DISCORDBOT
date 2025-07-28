from discord.ext import commands

@commands.command()
async def join(ctx):
    """
    Komenda dołączająca bota do kanału głosowego użytkownika.
    """
    if ctx.author.voice:
        channel = ctx.author.voice.channel

        # Jeśli bot już jest na tym samym kanale
        if ctx.voice_client and ctx.voice_client.channel == channel:
            await ctx.send("Bot już znajduje się na tym kanale głosowym.")
            return

        try:
            # Jeśli bot jest gdzie indziej – przenieś go
            if ctx.voice_client:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()

            await ctx.send(f"Połączono z kanałem: {channel.name}")
        except Exception as e:
            await ctx.send(f"Nie udało się dołączyć do kanału: {e}")
    else:
        await ctx.send("Musisz najpierw dołączyć do kanału głosowego, aby bot mógł dołączyć.")
