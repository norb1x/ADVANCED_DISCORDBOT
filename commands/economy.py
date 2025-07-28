import aiosqlite
import asyncio

class EconomyManager:
    """
    Klasa zarządzająca prostą ekonomią użytkowników (saldo wirtualnej waluty).
    """

    def __init__(self, db_path="economy.db"):
        self.db_path = db_path
        # Tworzenie tabeli w tle przy starcie
        asyncio.create_task(self._init_db())

    async def _init_db(self):
        """
        Inicjalizuje bazę danych (tworzy tabelę users jeśli nie istnieje).
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    balance INTEGER DEFAULT 1000
                )
            ''')
            await db.commit()

    async def get_balance(self, user_id):
        """
        Pobiera saldo użytkownika.
        Jeśli nie ma rekordu – zwraca domyślnie 1000.
        """
        user_id = str(user_id)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT balance FROM users WHERE user_id = ?", 
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else 1000

    async def update_balance(self, user_id, amount):
        """
        Aktualizuje saldo użytkownika.
        Jeśli rekord nie istnieje, tworzy go z początkowym saldem 1000.
        Saldo nie może spaść poniżej zera.
        """
        user_id = str(user_id)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO users (user_id, balance)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET balance = MAX(balance + ?, 0)
            ''', (user_id, 1000, amount))
            await db.commit()
