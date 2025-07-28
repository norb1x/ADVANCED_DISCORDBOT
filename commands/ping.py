import requests
from discord.ext import commands

@commands.command()
async def ping(ctx, url: str = "https://www.google.com"):
    """
    Sprawdza dostępność strony (HTTP GET) i zwraca status.
    """
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url
    try:
        response = requests.get(url, timeout=5)
        await ctx.send(f"Status dla {url}: {response.status_code} {response.reason}")
    except requests.RequestException as e:
        await ctx.send(f"Nie udało się połączyć z {url}. Błąd: {e}")
