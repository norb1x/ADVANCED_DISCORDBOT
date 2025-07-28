import aiosqlite

DB_PATH = "bot_database.db"

async def init_db():
    """
    Tworzy tabele w bazie danych (jeśli nie istnieją).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS voice_time (
                user_id INTEGER PRIMARY KEY,
                display_name TEXT,
                total_seconds REAL DEFAULT 0
            )
        ''')
        await db.commit()

async def get_balance(user_id: int) -> int:
    """
    Pobiera saldo użytkownika.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT balance FROM users WHERE user_id = ?", 
            (user_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

async def add_balance(user_id: int, amount: int):
    """
    Dodaje środki do konta użytkownika (lub tworzy rekord jeśli go brak).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO users (user_id, balance)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?
        ''', (user_id, amount, amount))
        await db.commit()

async def add_voice_time(user_id: int, display_name: str, seconds: float):
    """
    Dodaje czas spędzony na kanale głosowym do statystyk użytkownika.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO voice_time (user_id, display_name, total_seconds)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
                total_seconds = total_seconds + ?,
                display_name = excluded.display_name
        ''', (user_id, display_name, seconds, seconds))
        await db.commit()

async def get_voice_ranking(limit: int = 5):
    """
    Zwraca listę użytkowników z największą ilością czasu na kanałach głosowych.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT display_name, total_seconds
            FROM voice_time
            ORDER BY total_seconds DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()
