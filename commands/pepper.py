import feedparser
import discord
import re
import requests
import json
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from datetime import datetime

# Zamaskowany ID kanału – w prywatnym repozytorium podaj właściwy
CHANNEL_ID = ****  

class Pepper(commands.Cog):
    """
    Cog odpowiedzialny za pobieranie i publikowanie najnowszych gorących ofert z pepper.pl.
    """

    def __init__(self, bot):
        self.bot = bot
        self.send_pepper.start()

    def cog_unload(self):
        self.send_pepper.cancel()

    @commands.command()
    async def pepper(self, ctx):
        """
        Ręczne wywołanie komendy pobierającej aktualne TOP 10 okazji.
        """
        await self.send_top10(ctx.channel)

    def get_price_from_rss_item(self, item_xml):
        """
        Próbuje pobrać cenę z elementu RSS (XML).
        """
        try:
            soup = BeautifulSoup(item_xml, "xml")
            merchant = soup.find("pepper:merchant")
            if merchant and merchant.has_attr("price"):
                cena = merchant["price"]
                print(f"[DEBUG] Cena z RSS XML: {cena}")
                return cena + " zł"
        except Exception as e:
            print(f"[BŁĄD] Parsowanie RSS item: {e}")
        return None

    def get_price_from_pepper(self, link):
        """
        Próbuje wyciągnąć cenę bezpośrednio z treści strony Pepper.
        """
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # 1. Cena z elementu .thread-price
            price_element = soup.select_one(".thread-price")
            if price_element:
                price_text = price_element.get_text(strip=True).lower()
                price_text = price_text.replace("pln", "zł")
                print(f"[DEBUG] Cena z .thread-price: {price_text} ({link})")
                return price_text

            # 2. Cena z tekstu strony
            text = soup.get_text(separator=' ', strip=True).lower()
            full_matches = re.findall(r"(\d{1,5}[.,]?\d{0,2})\s?(zł|pln)", text)
            if full_matches:
                cena = f"{full_matches[0][0].replace(',', '.')} {full_matches[0][1].replace('pln', 'zł')}"
                print(f"[DEBUG] Cena z treści strony: {cena} ({link})")
                return cena

            # 3. Cena z meta tagów
            for meta in soup.find_all("meta"):
                content = meta.get("content", "").lower()
                match = re.search(r"\d{1,5}[.,]?\d{0,2}\s?(zł|pln)", content)
                if match:
                    cena = match.group(0).replace(",", ".").replace("pln", "zł")
                    print(f"[DEBUG] Cena z meta tagu: {cena} ({link})")
                    return cena

            # 4. Cena z JSON-LD
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        offers = data.get("offers")
                        if isinstance(offers, dict) and "price" in offers:
                            price = str(offers["price"]).replace(",", ".")
                            currency = offers.get("priceCurrency", "zł").replace("pln", "zł")
                            cena = f"{price} {currency}"
                            print(f"[DEBUG] Cena z JSON-LD: {cena} ({link})")
                            return cena
                except Exception:
                    continue

            # 5. Cena z raw HTML
            raw_html = soup.prettify().lower()
            match = re.search(r"\d{1,5}[.,]?\d{0,2}\s?(zł|pln)", raw_html)
            if match:
                cena = match.group(0).replace(",", ".").replace("pln", "zł")
                print(f"[DEBUG] Cena z raw HTML: {cena} ({link})")
                return cena

            print(f"[DEBUG] Nie znaleziono ceny: {link}")
            return "brak ceny"

        except Exception as e:
            print(f"[BŁĄD] Podczas pobierania {link}: {e}")
            return "brak ceny"

    async def send_top10(self, channel):
        """
        Wysyła wiadomość embed z TOP 10 gorącymi okazjami z Pepper.pl.
        """
        feed = feedparser.parse("https://www.pepper.pl/rss/hot")
        entries = feed.entries[:10]

        embed = discord.Embed(
            title="🔥 TOP 10 z Pepper.pl (Hot)",
            description="Najgorętsze okazje z ostatnich godzin 🔥💸",
            color=discord.Color.orange()
        )

        embed.set_footer(text="Źródło: pepper.pl")
        embed.set_thumbnail(url="https://i.imgur.com/U26XvyE.png")

        for i, entry in enumerate(entries, 1):
            title = entry.title
            temp_match = re.search(r"\b\d+°", title)
            temp = temp_match.group(0) if temp_match else "?"

            price = self.get_price_from_rss_item(entry.get("summary", ""))
            if not price or "brak" in price:
                price = self.get_price_from_pepper(entry.link)

            embed.add_field(
                name=f"{i}. {title}",
                value=(
                    f"🔗 [Zobacz okazję]({entry.link})\n"
                    f"💰 **Cena:** `{price}`\n"
                    f"🔥 **Lajki:** `{temp}`"
                ),
                inline=False
            )

        await channel.send(embed=embed)

    @tasks.loop(minutes=5)
    async def send_pepper(self):
        """
        Automatyczne wysyłanie wiadomości z TOP 10 okazjami o określonych godzinach.
        """
        now = datetime.now()
        if now.hour in [8, 20] and now.minute < 5:
            channel = self.bot.get_channel(CHANNEL_ID)
            if channel:
                await self.send_top10(channel)

    @send_pepper.before_loop
    async def before_pepper(self):
        await self.bot.wait_until_ready()
