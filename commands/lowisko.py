import asyncio
import random
from discord.ext import commands
from .economy import EconomyManager

class Lowisko(commands.Cog):
    """
    Mini gra: łowienie ryb (gra na szybkość pisania).
    """

    def __init__(self, bot):
        self.bot = bot
        self.economy = EconomyManager()

    @commands.command()
    async def fish(self, ctx):
        """
        Rozpoczyna grę łowienia ryb.
        Użytkownik musi szybko przepisać tekst, aby zdobyć nagrodę.
        """
        fishes = [
            ("Mała rybka", "powolna rybka", "rybka", 5),
            ("Średnia ryba", "szybka i zwinna",
             "rybcia taka szybka, spróbuj szybko napisać to zdanie bez błędów", 10),
            ("Duża ryba", "silna i waleczna",
             "wielka ryba do złowienia, szybko wpisz dokładnie cały ten tekst, nie popełniając błędów, bo ona ucieknie w mgnieniu oka", 30),
            ("GIGA ryba", "bardzo silna i wymagająca",
             "gigantyczna ryba do złowienia, wpisz dokładnie ten tekst, nie myląc się ani razu, bo inaczej ucieknie", 60),
            ("Mutant", "bardzo trudna do złowienia", None, 120),
        ]

        name, desc, text_to_type, difficulty = random.choice(fishes)

        # Specjalny tekst dla mutanta
        if name == "Mutant":
            text_to_type = random.choice([
                "To jest wyjątkowy mutant, przepisz ten tekst bez błędów, każde słowo się liczy.",
                "Mutant nie lubi wolnych graczy, pisz szybko i dokładnie.",
                "Mutant sprawdza refleks, przepisz wszystko bez literówki!",
                "Bardzo trudne zadanie – przepisz cały tekst bez pomyłek.",
                "Wyjątkowo trudne wyzwanie – liczy się szybkość i dokładność."
            ])

        # Limit czasu zależy od długości tekstu
        time_limit = max(len(text_to_type) * 0.2, 5)

        animation_frames = ["🎣", "🛶", "🌊", "🐟", "⏳"]
        msg = await ctx.send(
            f"Łowienie: **{name}** - {desc}\n"
            f"Napisz ten tekst w ciągu {time_limit:.1f} sekund:\n`{text_to_type}`\n"
            f"Animacja: {animation_frames[0]}"
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        async def animate_message():
            for i in range(1, len(animation_frames)):
                await asyncio.sleep(time_limit / len(animation_frames))
                try:
                    await msg.edit(
                        content=(
                            f"Łowienie: **{name}** - {desc}\n"
                            f"Napisz ten tekst w ciągu {time_limit:.1f} sekund:\n`{text_to_type}`\n"
                            f"Animacja: {animation_frames[i]}"
                        )
                    )
                except:
                    break

        animation_task = asyncio.create_task(animate_message())

        try:
            start = self.bot.loop.time()
            user_msg = await self.bot.wait_for('message', timeout=time_limit, check=check)
            end = self.bot.loop.time()
            animation_task.cancel()
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, nie zdążyłeś wpisać tekstu na czas! 🎣")
            return

        time_taken = end - start
        typed_text = user_msg.content.strip()

        # Antycheat: zbyt szybka reakcja = podejrzenie wklejenia tekstu
        if time_taken < 0.7:
            await ctx.send(f"{ctx.author.mention} Reakcja była zbyt szybka – wygląda na wklejenie. Brak nagrody.")
            return

        if typed_text.lower() == text_to_type.lower():
            speed_cps = len(text_to_type) / time_taken
            speed_wpm = (len(text_to_type.split()) / time_taken) * 60
            await self.economy.update_balance(ctx.author.id, difficulty)
            await ctx.send(
                f"{ctx.author.mention} Złowiłeś **{name}**! 🎉\n"
                f"Czas: {time_taken:.2f}s\n"
                f"Szybkość: {speed_cps:.2f} znaków/s ({speed_wpm:.2f} słów/min)\n"
                f"Nagroda: {difficulty} 💰"
            )
        else:
            await ctx.send(f"{ctx.author.mention} Tekst nie zgadzał się. Spróbuj ponownie. 🎣")

def setup(bot):
    bot.add_cog(Lowisko(bot))
