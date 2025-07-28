import random
from discord.ext import commands
from .economy import EconomyManager

class Slots(commands.Cog):
    """
    Mini gra – sloty (jednoręki bandyta).
    """

    def __init__(self, bot):
        self.bot = bot
        self.economy = EconomyManager()

    @commands.command(aliases=["kibel"])
    async def slot(self, ctx, bet: str):
        """
        Gra w sloty.
        Możesz podać kwotę lub słowo 'kibel' aby postawić cały swój balans.
        """
        user_id = ctx.author.id
        balance = await self.economy.get_balance(user_id)

        # all-in jeśli wpisano "kibel"
        is_kibel = bet.lower() == "kibel"

        if is_kibel:
            bet_amount = balance
        else:
            try:
                bet_amount = int(bet)
            except ValueError:
                await ctx.send("Podaj poprawną liczbę albo wpisz `kibel`, aby postawić cały balans.")
                return

        if bet_amount <= 0:
            await ctx.send("Kwota musi być większa niż 0.")
            return

        if bet_amount > balance:
            await ctx.send(f"Nie masz tylu środków. Twój balans: {balance} 💰")
            return

        # losowanie symboli
        symbols = ["🍒", "🍋", "🔔", "🍇", "💎", "7️⃣"]
        result = [random.choice(symbols) for _ in range(3)]
        slot_result = " | ".join(result)

        # komunikat z wynikiem
        if is_kibel:
            await ctx.send(
                f"{ctx.author.mention} **ALL-IN**\n🎰 {slot_result} 🎰\n"
                f"Postawiłeś wszystko: {bet_amount} 💰"
            )
        else:
            await ctx.send(f"{ctx.author.mention} 🎰 {slot_result} 🎰")

        # sprawdzenie wyniku
        if result[0] == result[1] == result[2]:
            # jackpot – 3 takie same symbole
            win_amount = bet_amount * 5
            await self.economy.update_balance(user_id, win_amount)
            new_balance = await self.economy.get_balance(user_id)

            await ctx.send(
                f"💰 JACKPOT! Wygrałeś {win_amount} 💰! Twój nowy balans: {new_balance}"
            )

        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            # dwa takie same symbole
            win_amount = bet_amount * 2
            await self.economy.update_balance(user_id, win_amount)
            new_balance = await self.economy.get_balance(user_id)

            await ctx.send(
                f"🎉 Dwa takie same! Wygrałeś {win_amount} 💰! Twój nowy balans: {new_balance}"
            )

        else:
            # przegrana
            await self.economy.update_balance(user_id, -bet_amount)
            new_balance = await self.economy.get_balance(user_id)

            await ctx.send(
                f"😢 Brak wygranej. Straciłeś {bet_amount} 💰. Twój nowy balans: {new_balance}"
            )

        # sprawdzenie czy użytkownik ma saldo 0
        final_balance = await self.economy.get_balance(user_id)
        if final_balance == 0:
            await ctx.send(
                f"{ctx.author.mention} Twoje saldo wynosi teraz 0 💀.\n"
                f"Aby zdobyć środki, użyj komendy *fish."
            )

    @commands.command()
    async def balance(self, ctx):
        """
        Wyświetla aktualny balans użytkownika.
        """
        bal = await self.economy.get_balance(ctx.author.id)
        await ctx.send(f"{ctx.author.mention}, Twój balans: {bal} 💰")

async def help_slots(self, ctx):
    """
    Pomoc dotycząca komend dostępnych w module Slots.
    """
    commands_list = ", ".join([cmd.name for cmd in self.get_commands()])
    await ctx.send(f"Dostępne komendy w Slots: {commands_list}")

def setup(bot):
    bot.add_cog(Slots(bot))
