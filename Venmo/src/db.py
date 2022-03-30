import os
import sqlite3
import time

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the instance variable "conn"
        """
        self.conn = sqlite3.connect("venmo.db", check_same_thread = False)
        self.create_users_table()
        self.create_transactions_table()

    def create_users_table(self):
        """
        Using SQL, creates a task table
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER NOT NULL
                );
                """
            )
        except Exception as e:
            print(e)

    def create_transactions_table(self):
        """
        Using SQL, create a transactions table
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE trnxs(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount INTEGER NOT NULL,
                    accepted BOOL NULLABLE,
                    message TEXT NOT NULL,
                    sender_id INTEGER SECONDARY KEY NOT NULL,
                    receiver_id INTEGER SECONDARY KEY NOT NULL
                );
                """
            )
        except Exception as e:
            print(e)
        
    def get_all_users(self):
        """
        Using SQL, gets all users in the users table
        """
        cursor = self.conn.execute("SELECT id, name, username FROM users;")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})

        return users

    def insert_user_table(self, name, username, balance):
        """
        Using SQL, adds a new user in the users table
        """
        cursor = self.conn.execute("INSERT INTO users (name, username, balance) VALUES (?, ?, ?);", (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid
    
    def insert_transactions_table(self, sender_id, receiver_id, amount, accepted, message):
        """
        Using SQL, adds a new transaction in the transactions table
        """
        cursor = self.conn.execute("INSERT INTO trnxs (sender_id, receiver_id, amount, accepted, message) VALUES (?, ?, ?, ?, ?);", (sender_id, receiver_id, amount, accepted, message))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_transaction(self, id):
        """
        Using SQL, get transactions responses
        """
        cursor = self.conn.execute("SELECT * FROM trnxs WHERE id = ?;", (id,))
        for row in cursor:
            if row[2] is None:
                return {"id": row[0], "timestamp": time.asctime(), "amount": row[1], "accepted": None, "sender_id": row[4], "receiver_id": row[5], "message": row[3]}
            return {"id": row[0], "timestamp": time.asctime(), "amount": row[1], "accepted": bool(row[2]), "sender_id": row[4], "receiver_id": row[5], "message": row[3]}


    def update_transaction(self, accepted, id):
        """
        Using SQL, update transaction
        """
        self.conn.execute("UPDATE trnxs SET accepted = ? WHERE id = ?;", (accepted, id))
        self.conn.commit()

    def get_user_id(self, id):
        """
        Using SQL, get a user by their id
        """
        list = []
        cursor1 = self.conn.execute("SELECT * FROM trnxs WHERE sender_id = ? OR receiver_id = ?;", (id, id))
        for row1 in cursor1:
            list.append(self.get_transaction(row1[0]))
        cursor = self.conn.execute("SELECT * FROM users WHERE id = ?;", (id,))
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3], "transactions": list}

    def delete_user_id(self, id):
        """
        Using SQL, delete user by its id
        """
        self.conn.execute("DELETE FROM users WHERE id=?;", (id,))
        self.conn.commit()

    def get_balance_id(self, id):
        """
        Using SQL, get balance of a user
        """
        cursor = self.conn.execute("SELECT balance FROM users WHERE id = ?;", (id,))
        for row in cursor:
            return row[0]


    def update_balance_id(self, sndr_id, rcvr_id, amnt):
        """
        Using SQL, exchange money between two users
        """
        self.conn.execute("UPDATE users SET balance = balance - ? WHERE id=?;", (amnt, sndr_id))
        self.conn.execute("UPDATE users SET balance= balance + ? WHERE id=?;", (amnt, rcvr_id))
        self.conn.commit()


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
