from discord.ext import commands, tasks
import discord
from .economy import EconomyManager  # import z twojego pliku economy.py

class ActivityRewarder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.economy = EconomyManager()
        self.reward_active_users.start()

    def cog_unload(self):
        self.reward_active_users.cancel()

    @tasks.loop(hours=1)
    async def reward_active_users(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.bot and member.status != discord.Status.offline:
                    await self.economy.update_balance(member.id, 100)

    @reward_active_users.before_loop
    async def before_reward(self):
        await self.bot.wait_until_ready()

    @commands.command(name="addbalance")
    async def add_balance(self, ctx, member: discord.Member, amount: int):
        owner_id = ****  # ukryte ID właściciela

        if ctx.author.id != owner_id:
            await ctx.send("❌ Brak uprawnień do tej komendy.")
            return

        if amount <= 0:
            await ctx.send("Kwota musi być większa niż 0.")
            return

        await self.economy.update_balance(member.id, amount)
        new_balance = await self.economy.get_balance(member.id)

        if new_balance == 0:
            await ctx.send(f"{member.mention} nadal ma 0💰.")
        else:
            await ctx.send(f"{member.mention} otrzymał {amount}💰. Nowe saldo: {new_balance}💰.")

def setup(bot):
    bot.add_cog(ActivityRewarder(bot))
