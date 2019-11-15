import sqlite3


class Db:
    def __init__(self,
                 name: str = 'reports.db'):
        self.name = name
        self.conn = None
        self.cursor = None

    def __create_db(self):
        # 15 columns
        self.cursor.execute("""CREATE TABLE reports (debt_name, creditor, type, ecoa, account_number, push,
        last_collector, collector_account, last_debt_status, bureaus, days_delinquent, balance_original, payment_amount,
        credit_limit, graduation)""")

    def connect(self):
        # if os.path.isfile(self.name):
        self.conn = sqlite3.connect(self.name)
        self.cursor = self.conn.cursor()

    def insert_row(self, row: list):
        assert len(row) == 15
        self.cursor.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )", row)
        self.conn.commit()

