import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta



load_dotenv(".env")

def create_connection():
    try:
        cnx = mysql.connector.connect(user='root', password='My_Password',
                                      host='localhost',
                                      database='expense_tracker')
        return cnx
    except Error as e:
        print(f"Error: {e}")
        return None

def close_connection(cnx):
    if cnx:
        cnx.close()

def create_tables():
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()

            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    number VARCHAR(20) UNIQUE NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    threshold DECIMAL(10, 2) NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    reason VARCHAR(255) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenues (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    reason VARCHAR(255) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL
                )
            """)

            cnx.commit()
            print("Tables created successfully!")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)


def insert_user(username, password, email, number):
    print("Creating user")
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "INSERT INTO users (username, password, email, number) VALUES (%s, %s, %s, %s)"
            data = (username, password, email, number)
            cursor.execute(query, data)
            cnx.commit()
            print("User inserted successfully!")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)

def authenticate(username, password):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            data = (username, password)
            cursor.execute(query, data)
            result = cursor.fetchone()
            return result is not None
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)
    return False

create_tables()

def login(username, password):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            data = (username, password)
            cursor.execute(query, data)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)
    return None

def signup(email, number, username, password):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "INSERT INTO users (email, number, username, password) VALUES (%s, %s, %s, %s)"
            data = (email, number, username, password)
            cursor.execute(query, data)
            cnx.commit()
            print("User signed up successfully!")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)

def check_user_existence(username=None, email=None, number=None):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            conditions = []
            data = []
            
            if username is not None:
                conditions.append("username = %s")
                data.append(username)
                
            if email is not None:
                conditions.append("email = %s")
                data.append(email)
                
            if number is not None:
                conditions.append("number = %s")
                data.append(number)

            query = f"SELECT * FROM users WHERE {' AND '.join(conditions)}"
            cursor.execute(query, tuple(data))
            result = cursor.fetchone()
            return result is not None
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)
    return False

def get_all_emails():
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "SELECT email FROM users"
            cursor.execute(query)
            result = cursor.fetchall()
            return [record[0] for record in result]
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)
    return []

def get_all_usernames():
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "SELECT username FROM users"
            cursor.execute(query)
            result = cursor.fetchall()
            return [record[0] for record in result]
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)
    return []

def get_all_numbers():
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "SELECT number FROM users"
            cursor.execute(query)
            result = cursor.fetchall()
            return [record[0] for record in result]
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)
    return []

def set_budget(username, amount, threshold):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "INSERT INTO budgets (username, budget_amount, threshold) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE budget_amount = %s, threshold = %s"
            data = (username, amount, threshold, amount, threshold)
            cursor.execute(query, data)
            cnx.commit()
            print("Budget set successfully!")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)


def get_budget(username):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            query = "SELECT budget_amount, threshold FROM budgets WHERE username = %s"
            data = (username,)
            cursor.execute(query, data)
            result = cursor.fetchone()
            return result if result else None
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)
    return None


def insert_expense(username, date, reason, amount):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")

            cnx.start_transaction()

            try:
                query_expense = "INSERT INTO expenses (username, date, reason, amount) VALUES (%s, %s, %s, %s)"
                data_expense = (username, formatted_date, reason, amount)
                cursor.execute(query_expense, data_expense)
                query_budget = "UPDATE budgets SET budget_amount = budget_amount - %s WHERE username = %s"

                data_budget = (amount, username)
                cursor.execute(query_budget, data_budget)
                cnx.commit()
                print("Expense entry added successfully!")
            except Error as e:
                cnx.rollback()
                print(f"Transaction failed. Error: {e}")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)

def insert_revenue(username, date, reason, amount):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()
            formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")

            cnx.start_transaction()

            try:
                query_revenue = "INSERT INTO revenues (username, date, reason, amount) VALUES (%s, %s, %s, %s)"
                data_revenue = (username, formatted_date, reason, amount)
                cursor.execute(query_revenue, data_revenue)
                query_budget = "UPDATE budgets SET budget_amount = budget_amount + %s WHERE username = %s"
                data_budget = (amount, username)
                cursor.execute(query_budget, data_budget)

                cnx.commit()
                print("Revenue entry added successfully!")
            except Error as e:
                cnx.rollback()
                print(f"Transaction failed. Error: {e}")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)


def get_user_transactions(username):
    cnx = create_connection()
    if cnx:
        try:
            cursor = cnx.cursor()

            query_expenses = """
                SELECT date, reason, amount
                FROM expenses
                WHERE username = %s AND date >= CURDATE() - INTERVAL 30 DAY
                ORDER BY date DESC
            """
            data = (username,)
            cursor.execute(query_expenses, data)
            expenses = cursor.fetchall()

            query_revenues = """
                SELECT date, reason, amount
                FROM revenues
                WHERE username = %s AND date >= CURDATE() - INTERVAL 30 DAY
                ORDER BY date DESC
            """
            cursor.execute(query_revenues, data)
            revenues = cursor.fetchall()

            print("Expenses:", expenses)
            print("Revenues:", revenues)

            return expenses, revenues
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(cnx)
    return None, None

# insert_expense("mrdev","15/11/2023","Canteen",50)
#insert user working for creating new users
#authrnticate working for login