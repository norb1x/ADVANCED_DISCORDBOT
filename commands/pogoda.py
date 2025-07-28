import discord
from discord.ext import commands
import requests
from datetime import datetime, timedelta
import pytz

# Klucz API – w publicznym repozytorium zaleca się użycie pliku konfiguracyjnego
API_KEY = "****"

DNI_TYGODNIA = {
    "poniedzialek": 0,
    "wtorek": 1,
    "sroda": 2,
    "czwartek": 3,
    "piatek": 4,
    "sobota": 5,
    "niedziela": 6,
    "jutro": (datetime.now() + timedelta(days=1)).weekday(),
    "teraz": -1,
    "5dni": -2
}

class Pogoda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["prognoza"])
    async def pogoda(self, ctx, *, args: str):
        """
        Wyświetla prognozę pogody dla wybranego miasta.
        Obsługiwane formaty:
        *pogoda miasto
        *pogoda jutro miasto
        *pogoda 5dni miasto
        """
        args = args.lower().strip().split()
        if len(args) == 1:
            dzien, miasto = "teraz", args[0]
        elif args[0] in DNI_TYGODNIA:
            dzien, miasto = args[0], " ".join(args[1:])
        else:
            dzien, miasto = "teraz", " ".join(args)

        # Geolokalizacja miasta
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={miasto}&limit=1&appid={API_KEY}"
        geo_response = requests.get(geo_url)
        if geo_response.status_code != 200 or not geo_response.json():
            await ctx.send("❌ Nie znaleziono miasta – sprawdź pisownię.")
            return

        geo_data = geo_response.json()[0]
        lat, lon = geo_data["lat"], geo_data["lon"]
        nazwamiasta = geo_data["name"]

        if dzien == "teraz":
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&lang=pl&units=metric"
            data = requests.get(url).json()
            temp = data['main']['temp']
            warunki = data['weather'][0]['description']
            ikonka = data['weather'][0]['icon']
            wiatr = data['wind'].get('speed', 0)
            wilgotnosc = data['main'].get('humidity', 0)

            ostrzezenie = ocena_pogody(warunki, temp, wiatr, wilgotnosc)

            embed = discord.Embed(
                title=f"🌤️ Pogoda TERAZ w {nazwamiasta}",
                description=f"{warunki.capitalize()}, {temp}°C",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{ikonka}@2x.png")
            embed.add_field(name="Ocena", value=ostrzezenie)
            await ctx.send(embed=embed)
            return

        # POBIERZ PROGNOZĘ (forecast)
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&lang=pl&units=metric"
        forecast_data = requests.get(forecast_url).json()
        lista = forecast_data["list"]

        if dzien == "5dni":
            grouped = {}
            for e in lista:
                ts = datetime.utcfromtimestamp(e["dt"]) + timedelta(hours=2)
                day = ts.strftime("%A")
                grouped.setdefault(day, []).append(e)

            tlumaczenia_dni = {
                "Monday": "Poniedziałek",
                "Tuesday": "Wtorek",
                "Wednesday": "Środa",
                "Thursday": "Czwartek",
                "Friday": "Piątek",
                "Saturday": "Sobota",
                "Sunday": "Niedziela"
            }

            desc = ""
            for day, entries in list(grouped.items())[:5]:
                temps = [e["main"]["temp"] for e in entries]
                min_temp = round(min(temps), 1)
                max_temp = round(max(temps), 1)
                avg_temp = round(sum(temps) / len(temps), 1)

                winds = [e["wind"]["speed"] for e in entries]
                humidities = [e["main"]["humidity"] for e in entries]
                avg_wind = round(sum(winds) / len(winds), 1)
                avg_hum = round(sum(humidities) / len(humidities), 1)

                warunki = entries[0]['weather'][0]['description']
                reakcja = ocena_pogody(warunki, avg_temp, avg_wind, avg_hum)

                dzien_pl = tlumaczenia_dni.get(day, day)

                desc += (
                    f"📅 **{dzien_pl}**\n"
                    f"🌡️ Temp: {avg_temp}°C (min {min_temp}°C / max {max_temp}°C)\n"
                    f"🌬️ Wiatr: {avg_wind} m/s\n"
                    f"💦 Wilgotność: {avg_hum}%\n"
                    f"🌥️ Warunki: {warunki.capitalize()}\n"
                    f"🧠 Ocena: {reakcja}\n\n"
                )

            embed = discord.Embed(title=f"📆 Prognoza 5-dniowa: {nazwamiasta}", description=desc, color=discord.Color.orange())
            await ctx.send(embed=embed)
            return

        # Forecast na konkretny dzień
        target_day = DNI_TYGODNIA.get(dzien, -1)
        if target_day == -1:
            await ctx.send("❌ Nie rozumiem o jaki dzień chodzi.")
            return

        today = datetime.now(pytz.timezone("Europe/Warsaw")).weekday()
        delta = (target_day - today + 7) % 7
        target_date = (datetime.now() + timedelta(days=delta)).date()

        dzienne = [e for e in lista if (datetime.utcfromtimestamp(e["dt"]) + timedelta(hours=2)).date() == target_date]

        if not dzienne:
            await ctx.send("❌ Nie mam prognozy na ten dzień.")
            return

        temps = [e["main"]["temp"] for e in dzienne]
        min_temp = round(min(temps), 1)
        max_temp = round(max(temps), 1)
        avg_temp = round(sum(temps) / len(temps), 1)

        warunki = dzienne[0]["weather"][0]["description"]
        ikonka = dzienne[0]["weather"][0]["icon"]

        reakcja = ocena_pogody(warunki, avg_temp)

        embed = discord.Embed(
            title=f"📆 Pogoda na {dzien.capitalize()} – {nazwamiasta}",
            description=(
                f"🌥️ Warunki: {warunki.capitalize()}\n"
                f"🌡️ Temp: {avg_temp}°C (min {min_temp}°C / max {max_temp}°C)\n"
                f"🧠 Ocena: {reakcja}"
            ),
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{ikonka}@2x.png")
        await ctx.send(embed=embed)

def ocena_pogody(warunki, temp, wiatr=0, wilgotnosc=0):
    """
    Prosta ocena pogody na podstawie warunków.
    """
    warunki = warunki.lower()
    if any(x in warunki for x in ['burza', 'ulewa', 'sztorm', 'śnieg']):
        return "⚠️ Uwaga: silne opady lub burze."
    elif temp > 30:
        return "🥵 Bardzo gorąco."
    elif temp < 0:
        return "🥶 Bardzo zimno."
    elif wiatr > 10:
        return "💨 Silny wiatr."
    elif wilgotnosc > 80:
        return "💦 Wysoka wilgotność powietrza."
    return "✅ Pogoda sprzyjająca."

async def setup(bot):
    await bot.add_cog(Pogoda(bot))
