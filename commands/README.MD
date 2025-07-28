# commands/

W tym katalogu znajdują się wszystkie moduły (cogi i komendy) używane przez bota Discord.  
Każdy plik odpowiada za osobną funkcjonalność.

---

## Spis plików i funkcjonalności

### Ekonomia i nagrody
- **economy.py**  
  - Obsługa bazy danych ekonomii (saldo użytkowników).
- **activity_reward.py**  
  - Automatyczne przyznawanie punktów użytkownikom aktywnym co godzinę.
  - Komenda administracyjna `*addbalance`.

### Gry i zabawa
- **slots.py**  
  - Gra w sloty (`*slot`, alias `*kibel` na all-in).
- **blackjack.py**  
  - Gra w blackjacka (`*blackjack`, `*hit`, `*stand`).
- **lowisko.py**  
  - Gra w łowienie ryb, polegająca na szybkim przepisaniu tekstu (`*fish`).

### Muzyka i audio
- **join.py / leave.py / play.py / playyt.py / restart.py**  
  - `*join` – dołącz do kanału głosowego  
  - `*leave` – opuść kanał  
  - `*play` – odtwarzanie radia (lokalne źródła)  
  - `*playyt` – odtwarzanie audio z YouTube za pomocą yt-dlp (**edukacyjne, nie wspierane przez Discord**)  
  - `*restart` – restart bota (dla adminów)

### RSS i dane zewnętrzne
- **pepper.py**  
  - Pobiera top 10 gorących okazji z pepper.pl.
- **stealalert_feed.py**  
  - Subskrypcja feeda RSS (przykładowy – **edukacyjny**).

### Pogoda
- **pogoda.py**  
  - `*pogoda [miasto]` – pogoda aktualna
  - `*pogoda jutro miasto` – prognoza na jutro
  - `*pogoda 5dni miasto` – prognoza 5-dniowa

### Inne funkcje
- **komendy.py**  
  - Wyświetla listę dostępnych komend (`*komendy`).
- **ping.py**  
  - Sprawdzenie odpowiedzi serwera przez HTTP (`*ping <adres>`).
- **logi.py**  
  - Logowanie aktywności na kanałach głosowych i ranking czasu spędzonego w VC.
- **database.py**  
  - Obsługa tabel SQLite (głosowe statystyki i ekonomia).

---

## Dodawanie nowych komend

1. Stwórz nowy plik `.py` w folderze `commands/`.
2. Zaimplementuj w nim klasę `commands.Cog` lub pojedynczą funkcję oznaczoną dekoratorem `@commands.command()`.
3. Upewnij się, że plik posiada funkcję:

```python
def setup(bot):
    bot.add_cog(MyCog(bot))
