import sqlite3

BASE_CATEGORIES = ['Food', 'Rent&Home', 'Transport', 'Pleasure']


class DataBase:
    """Connection to SQLite database."""

    def __init__(self, client_id=None) -> None:
        self.connection = sqlite3.connect('db/spendings.sqlite')
        self.cursor = self.connection.cursor()
        self.client_id = client_id

    def create_database(self):
        with self.connection:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS spendings(
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                date TEXT,
                category TEXT,
                amount REAL
            );
            ''')
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories(
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                category TEXT
            );
            ''')
        return True

    def categories_db_initialization(self):
        with self.connection:
            insert = [tuple((self.client_id, cat)) for cat in BASE_CATEGORIES]
            self.cursor.executemany('''
                INSERT INTO categories (client_id, category)
                VALUES(?, ?);
                ''', insert)

    def read_categories(self):
        with self.connection:
            self.cursor.execute('''
            SELECT category
            FROM categories
            WHERE client_id = ?
            ORDER BY category
            ''', (self.client_id,))
        return [cat[0] for cat in self.cursor]

    def add_category(self, category):
        with self.connection:
            self.cursor.execute('''
            INSERT INTO categories (client_id, category)
            VALUES(?, ?);
            ''', (self.client_id, category))
        return True

    def delete_category(self, category):
        with self.connection:
            self.cursor.execute('''
            DELETE FROM categories
            WHERE client_id = ?
            AND category = ?;
            ''', (self.client_id, category))
        return True

    def read_spendings_month(self):
        with self.connection:
            self.cursor.execute('''
            SELECT strftime('%d.%m %H:%M', date), category, amount
            FROM spendings
            WHERE client_id = ?
            AND date BETWEEN datetime('now', 'start of month')
            AND datetime('now', '1 hour')
            ORDER BY date;
            ''', (self.client_id,))
            answer = [f'*{date[:5]}*{date[5:]}*|* {category} `{amount:.2f}€`'
                      for date, category, amount in self.cursor]
        return answer

    def last_spend(self):
        with self.connection:
            self.cursor.execute('''
            SELECT id, strftime('%d.%m.%Y at %H:%M', date), category, amount
            FROM spendings
            WHERE client_id = ?
            ORDER BY date DESC
            LIMIT 1
            ''', (self.client_id,))
        return [cat for cat in self.cursor][0]

    def get_sum(self):
        with self.connection:
            self.cursor.execute('''
            SELECT SUM(amount)
            FROM spendings
            WHERE client_id = ? AND
            date BETWEEN datetime('now', 'start of month')
            AND datetime('now', '1 hour');
            ''', (self.client_id,))
        return round(self.cursor.fetchone()[0], 2)

    def get_sum_categories(self):
        with self.connection:
            self.cursor.execute('''
            SELECT category, SUM(amount) AS amounts
            FROM spendings
            WHERE client_id = ? AND
            date > date('now', 'start of month')
            GROUP BY category
            ORDER BY amounts DESC;
            ''', (self.client_id,))
            answer = [f'*{category}*: `{amount:.2f}€`'
                      for category, amount in self.cursor]
        return answer

    def new_spending(self, category, amount):
        with self.connection:
            transaction = (self.client_id, category, amount)
            self.cursor.execute('''
            INSERT INTO spendings (client_id, date, category, amount)
            VALUES(?, datetime('now', '1 hour'),?,?);
            ''', transaction)
        return True

    def delete_spend(self, id):
        with self.connection:
            self.cursor.execute(f'''
            DELETE FROM spendings
            WHERE id = {id};
            ''')
        return True

    def check_user_exist(self, table='categories'):
        with self.connection:
            self.cursor.execute(f'''
            SELECT EXISTS
            (SELECT * FROM {table}
            WHERE client_id = ?);
            ''', (self.client_id, ))
        return self.cursor.fetchone()[0]

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    pass
