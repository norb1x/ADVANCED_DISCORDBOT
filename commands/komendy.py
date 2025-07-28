import discord
from discord.ext import commands

class Komendy(commands.Cog):
    """
    Cog z komendą wyświetlającą listę dostępnych poleceń bota.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def komendy(self, ctx):
        """
        Wyświetla listę komend bota w formie osadzonej wiadomości (Embed).
        """
        embed = discord.Embed(
            title="📜 Lista komend bota",
            description="Dostępne funkcje i polecenia:",
            color=discord.Color.green()
        )

        embed.add_field(name="🌤️ *pogoda [miasto]", value="Sprawdza pogodę w podanym mieście.", inline=False)
        embed.add_field(name="🎧 *join", value="Dołączenie bota do kanału głosowego.", inline=False)
        embed.add_field(
            name="🎵 *play [link]",
            value=(
                "Odtwarza radio z wybranej listy (np. rmf_24, radio_lodz, radio_zet, "
                "czeskie_radio, czeski_jazz, radio_bielsko, radio_eska)."
            ),
            inline=False
        )
        embed.add_field(name="📺 *playyt [link]", value="Odtwarzanie z YouTube przy pomocy yt-dlp.", inline=False)
        embed.add_field(name="🛑 *leave", value="Bot opuszcza kanał głosowy.", inline=False)
        embed.add_field(name="🔁 *restart", value="Restart aktualnie odtwarzanego utworu.", inline=False)
        embed.add_field(name="📶 *ping <ip>", value="Sprawdzenie pingu dowolnego hosta.", inline=False)
        embed.add_field(name="💸 *slot [kwota]", value="Mini gra – sloty (jednoręki bandyta).", inline=False)
        embed.add_field(name="🃏 *blackjack", value="Mini gra – blackjack.", inline=False)
        embed.add_field(name="🐟 *fish", value="Mini gra – łowienie ryb (zdobądź punkty).", inline=False)
        embed.add_field(name="🌶️ *pepper", value="Wyświetla aktualne promocje i okazje.", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Komendy(bot))
