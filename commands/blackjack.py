import random
from discord.ext import commands
from .economy import EconomyManager  # async manager ekonomii

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.economy = EconomyManager()
        self.games = {}

    def deal_card(self):
        """Losuje pojedynczą kartę."""
        card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
        suits = ["♠️", "♥️", "♦️", "♣️"]
        value = random.choice(card_values)
        suit = random.choice(suits)
        if value == 11:
            card_str = f"🅰️{suit}"
        elif value == 10:
            fig = random.choice(["10", "J", "Q", "K"])
            card_str = f"{fig}{suit}"
        else:
            card_str = f"{value}{suit}"
        return (value, card_str)

    def calculate_score(self, hand):
        """Oblicza wynik gracza lub krupiera."""
        score = sum(card[0] for card in hand)
        aces = [card for card in hand if card[0] == 11]
        while score > 21 and aces:
            aces.pop()
            score -= 10
        return score

    def format_hand(self, hand):
        """Zwraca karty w postaci tekstowej."""
        return " ".join(card[1] for card in hand)

    @commands.command()
    async def blackjack(self, ctx, bet: int):
        """Rozpoczyna grę w blackjacka."""
        user_id = ctx.author.id
        balance = await self.economy.get_balance(user_id)

        if bet <= 0:
            await ctx.send("Musisz postawić kwotę większą niż 0.")
            return
        if bet > balance:
            await ctx.send(f"Nie masz wystarczających środków. Twój balans: {balance} 💰")
            return
        if user_id in self.games:
            await ctx.send(f"{ctx.author.mention}, masz już rozpoczętą grę! Użyj komend *hit lub *stand.")
            return

        # Odejmujemy stawkę od balansu
        await self.economy.update_balance(user_id, -bet)

        hand = [self.deal_card(), self.deal_card()]
        score = self.calculate_score(hand)
        self.games[user_id] = {"hand": hand, "score": score, "bet": bet}

        await ctx.send(f"{ctx.author.mention} Twoje karty: {self.format_hand(hand)} (suma: {score})")

        # Natychmiastowy blackjack
        if score == 21:
            win_amount = int(bet * 2.5)
            await self.economy.update_balance(user_id, win_amount)
            self.games.pop(user_id)
            new_balance = await self.economy.get_balance(user_id)
            await ctx.send(f"Blackjack! Wygrałeś {win_amount} 💰 🎉 Twój nowy balans: {new_balance}")

    @commands.command()
    async def hit(self, ctx):
        """Dobranie karty."""
        user_id = ctx.author.id
        if user_id not in self.games:
            await ctx.send(f"{ctx.author.mention}, nie masz aktywnej gry.")
            return

        hand = self.games[user_id]["hand"]
        bet = self.games[user_id]["bet"]
        hand.append(self.deal_card())
        score = self.calculate_score(hand)
        self.games[user_id]["score"] = score

        if score > 21:
            self.games.pop(user_id)
            new_balance = await self.economy.get_balance(user_id)
            await ctx.send(f"{ctx.author.mention} Przegrałeś. Karty: {self.format_hand(hand)} ({score}). Balans: {new_balance}")
        elif score == 21:
            win_amount = bet * 2
            await self.economy.update_balance(user_id, win_amount)
            self.games.pop(user_id)
            new_balance = await self.economy.get_balance(user_id)
            await ctx.send(f"{ctx.author.mention} Wygrałeś {win_amount} 💰! Balans: {new_balance}")
        else:
            await ctx.send(f"{ctx.author.mention} Karty: {self.format_hand(hand)} ({score}). Wpisz *hit aby dobrać kartę lub *stand aby zakończyć.")

    @commands.command()
    async def stand(self, ctx):
        """Zatrzymanie kart i ruch krupiera."""
        user_id = ctx.author.id
        if user_id not in self.games:
            await ctx.send(f"{ctx.author.mention}, nie masz aktywnej gry.")
            return

        player_score = self.games[user_id]["score"]
        bet = self.games[user_id]["bet"]

        # Krupier dobiera karty do 17 punktów
        dealer_hand = []
        dealer_score = 0
        while dealer_score < 17:
            card = self.deal_card()
            dealer_hand.append(card)
            dealer_score = self.calculate_score(dealer_hand)

        self.games.pop(user_id)

        result_msg = f"Karty krupiera: {self.format_hand(dealer_hand)} ({dealer_score}). Twoje: {player_score}.\n"

        if dealer_score > 21 or player_score > dealer_score:
            win_amount = bet * 2
            await self.economy.update_balance(user_id, win_amount)
            new_balance = await self.economy.get_balance(user_id)
            result_msg += f"{ctx.author.mention}, wygrałeś {win_amount} 💰! Balans: {new_balance}"
        elif player_score == dealer_score:
            await self.economy.update_balance(user_id, bet)
            new_balance = await self.economy.get_balance(user_id)
            result_msg += f"Remis. Stawka została zwrócona. Balans: {new_balance}"
        else:
            new_balance = await self.economy.get_balance(user_id)
            result_msg += f"{ctx.author.mention}, przegrałeś. Balans: {new_balance}"

        await ctx.send(result_msg)

def setup(bot):
    bot.add_cog(Blackjack(bot))
