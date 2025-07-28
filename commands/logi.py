import discord
from discord.ext import commands
from datetime import datetime
from .database import add_voice_time, get_voice_ranking  # korzystamy z jednej bazy i aiosqlite

# ID kanału logów (zamaskowane – w prywatnym repo wstaw swój)
LOG_CHANNEL_ID = ****  

class VoiceLogger(commands.Cog):
    """
    Cog odpowiedzialny za logowanie aktywności użytkowników
    na kanałach głosowych oraz zliczanie czasu spędzonego w VC.
    """

    def __init__(self, bot):
        self.bot = bot
        self.join_times = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            return

        timestamp = datetime.now().strftime("🕒 [%H:%M]")

        # Dołączenie na VC
        if not before.channel and after.channel:
            self.join_times[member.id] = datetime.now()
            await log_channel.send(
                f"{timestamp} 🔊 {member.display_name} dołączył do **{after.channel.name}**"
            )

        # Wyjście z VC
        elif before.channel and not after.channel:
            join_time = self.join_times.pop(member.id, None)
            if join_time:
                duration = (datetime.now() - join_time).total_seconds()
                await add_voice_time(member.id, member.display_name, duration)
            await log_channel.send(
                f"{timestamp} 🔇 {member.display_name} opuścił **{before.channel.name}**"
            )

        # Przeniesienie VC
        elif before.channel != after.channel:
            self.join_times[member.id] = datetime.now()
            await log_channel.send(
                f"{timestamp} 🔁 {member.display_name} przeniósł się z "
                f"**{before.channel.name}** do **{after.channel.name}**"
            )

        # Stream start
        if not before.self_stream and after.self_stream:
            await log_channel.send(
                f"{timestamp} 📺 {member.display_name} rozpoczął udostępnianie ekranu "
                f"na **{after.channel.name}**"
            )

        # Stream stop
        if before.self_stream and not after.self_stream:
            await log_channel.send(
                f"{timestamp} 🛑 {member.display_name} zakończył udostępnianie ekranu "
                f"na **{before.channel.name}**"
            )

    @commands.command(aliases=["rankingvc", "vctime"])
    async def ranking(self, ctx):
        """
        Wyświetla ranking użytkowników według czasu spędzonego
        na kanałach głosowych.
        """
        data = await get_voice_ranking()

        if not data:
            await ctx.send("Brak danych o aktywności głosowej.")
            return

        msg = "🎙️ **TOP użytkowników na kanałach głosowych:**\n"
        for i, (name, seconds) in enumerate(data, start=1):
            hours = int(seconds) // 3600
            minutes = (int(seconds) % 3600) // 60
            msg += f"{i}. **{name}** – {hours}h {minutes}m\n"

        await ctx.send(msg)
