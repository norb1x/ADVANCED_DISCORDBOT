# NOTE:
# This module demonstrates how to read data from an RSS/Atom feed and send it to a Discord channel.
# It is intended for EDUCATIONAL PURPOSES ONLY.
# Replace the placeholder RSS URL and channel ID with your own values in private projects.

import discord
from discord.ext import commands, tasks
import feedparser
import json
import os
from bs4 import BeautifulSoup

CHANNEL_ID = ****  # masked for public repo
RSS_URL = "****"   # masked for public repo
LAST_POST_FILE = "last_post.json"

class StealAlertFeed(commands.Cog):
    """
    Cog that fetches data from an RSS/Atom feed and posts updates in a Discord channel.
    """

    def __init__(self, bot):
        self.bot = bot
        self.last_post = self.load_last_post()
        self.check_feed.start()

    def load_last_post(self):
        if os.path.exists(LAST_POST_FILE):
            with open(LAST_POST_FILE, "r") as f:
                return json.load(f).get("url")
        return None

    def save_last_post(self, url):
        with open(LAST_POST_FILE, "w") as f:
            json.dump({"url": url}, f)

    @tasks.loop(minutes=5)
    async def check_feed(self):
        await self.fetch_and_send(force=False)

    async def fetch_and_send(self, force=False, ctx=None):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(CHANNEL_ID if not ctx else ctx.channel.id)
        if not channel:
            return

        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            if ctx:
                await ctx.send("❌ Brak wpisów w feedzie.")
            return

        latest = feed.entries[0]
        if force or latest.link != self.last_post:
            self.last_post = latest.link
            self.save_last_post(latest.link)

            soup = BeautifulSoup(latest.summary, "html.parser")
            clean_text = soup.get_text(separator="\n")[:1500]

            embed = discord.Embed(
                title=latest.title,
                url=latest.link,
                description=clean_text
            )

            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                embed.set_image(url=img_tag["src"])

            embed.set_footer(text="Źródło: RSS Feed")
            await channel.send(embed=embed)

        elif ctx and not force:
            await ctx.send("✅ Brak nowych wpisów. Feed jest aktualny.")

    @commands.command(name="stealnow")
    async def stealnow(self, ctx):
        """
        Ręczne wymuszenie pobrania i wyświetlenia najnowszego wpisu z feeda.
        """
        await self.fetch_and_send(force=True, ctx=ctx)

def setup(bot):
    bot.add_cog(StealAlertFeed(bot))
