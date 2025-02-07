import sqlite3

class Database:
    def __init__(self, name):
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Creates a table for storing scores if it doesn't exist."""
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                score INTEGER
            )'''
        )
        self.conn.commit()

    def save_score(self):
        """Save the player's score in the database."""
        self.cursor.execute("INSERT INTO scores (score) VALUES (?)", (self.cursor))
        self.conn.commit()

    def get_high_scores(self):
        """Retrieve the top 5 high scores."""
        self.cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 5")
        return self.cursor.fetchall()

    def close_db(self):
        """Close the database connection."""
        self.conn.close()
