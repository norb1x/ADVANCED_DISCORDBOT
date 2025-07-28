import discord
from discord.ext import commands
from config import TOKEN
from commands.slots import Slots
from commands.blackjack import Blackjack
from commands import join, play, playyt, leave, restart, ping
from commands.lowisko import Lowisko
from commands.pepper import Pepper
from commands.logi import VoiceLogger
from commands.pogoda import Pogoda
from commands.komendy import Komendy
from commands.database import init_db
from commands.stealalert_feed import StealAlertFeed
from commands.activity_reward import ActivityRewarder
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

# Ustawienia intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='*', intents=intents)

# ==========================
#  ANTY-SPAM
# ==========================
user_activity = defaultdict(list)
BLOCKED = set()

@bot.before_invoke
async def anti_spam(ctx):
    """Prosty globalny system antyspamowy."""
    user = ctx.author.id
    now = datetime.now()

    # Jeżeli użytkownik jest zablokowany
    if user in BLOCKED:
        raise commands.CommandError("Masz chwilową blokadę za spamowanie. Poczekaj chwilę i spróbuj ponownie.")

    # Logowanie użycia komend
    user_activity[user].append(now)

    # Czyści wpisy starsze niż 10 sekund
    user_activity[user] = [t for t in user_activity[user] if now - t < timedelta(seconds=10)]

    # Jeżeli w ciągu 10 sekund było więcej niż 5 komend – blokada na 30 s
    if len(user_activity[user]) > 5:
        BLOCKED.add(user)
        await ctx.send(f"{ctx.author.mention} wykryto spam – blokada na 30 sekund.")
        await asyncio.sleep(30)
        BLOCKED.remove(user)

# ==========================
#  Rejestracja komend
# ==========================
bot.add_command(join.join)
bot.add_command(play.play)
bot.add_command(playyt.playyt)
bot.add_command(leave.leave)
bot.add_command(restart.restart)
bot.add_command(ping.ping)

# ==========================
#  Event: on_ready
# ==========================
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

    # Ustawienie statusu bota
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="norb1x.app"
    ))

    await init_db()

    # Ładowanie cogów tylko raz
    if not hasattr(bot, 'loaded_cogs'):
        await bot.add_cog(Slots(bot))
        await bot.add_cog(Blackjack(bot))
        await bot.add_cog(Lowisko(bot))
        await bot.add_cog(Pepper(bot))
        await bot.add_cog(VoiceLogger(bot))
        await bot.add_cog(Pogoda(bot))
        await bot.add_cog(Komendy(bot))
        await bot.add_cog(StealAlertFeed(bot))
        await bot.add_cog(ActivityRewarder(bot))
        bot.loaded_cogs = True

# Uruchomienie bota
bot.run(TOKEN)
