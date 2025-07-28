# NOTE:
# Using direct YouTube audio streaming in Discord bots via yt_dlp and FFmpeg
# is not officially supported by Discord and may break at any time.
# This code is provided strictly for educational purposes.

import traceback
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp

@commands.command()
async def playyt(ctx, url: str):
    """
    Odtwarza audio z YouTube (lub innego źródła obsługiwanego przez yt_dlp).
    Funkcja tylko edukacyjna – Discord nie wspiera tego typu streamingu.
    """
    if not ctx.author.voice:
        await ctx.send("Musisz być na kanale głosowym.")
        return

    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        source = FFmpegPCMAudio(
            audio_url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        )
        ctx.voice_client.play(source)

        await ctx.send(f"Teraz gram: {info.get('title', 'nieznany tytuł')}")
    except Exception as e:
        await ctx.send(f"Coś poszło nie tak: {e}")
        traceback.print_exc()
