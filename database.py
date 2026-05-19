import sqlite3
import json
import os

DB_PATH = os.environ.get("RAILWAY_DATABASE_PATH", "database.sqlite")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_joint BOOLEAN,
                name TEXT NOT NULL,
                dob TEXT,
                ssn_last4 TEXT,
                salary_client1 REAL,
                spouse_name TEXT,
                spouse_dob TEXT,
                spouse_ssn_last4 TEXT,
                salary_client2 REAL,
                expense_budget REAL,
                insurance_deductibles REAL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                institution TEXT,
                acc_type TEXT,
                last4 TEXT,
                category TEXT NOT NULL,
                owner TEXT NOT NULL,
                last_known_balance REAL DEFAULT 0,
                interest_rate REAL DEFAULT 0,
                cash_balance REAL DEFAULT 0,
                address TEXT,
                FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                date TEXT NOT NULL,
                data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()

def create_client(data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (is_joint, name, dob, ssn_last4, salary_client1, spouse_name, spouse_dob, spouse_ssn_last4, salary_client2, expense_budget, insurance_deductibles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('is_joint', False), data.get('name'), data.get('dob'), data.get('ssn_last4'), data.get('salary_client1', 0),
            data.get('spouse_name'), data.get('spouse_dob'), data.get('spouse_ssn_last4'), data.get('salary_client2', 0),
            data.get('expense_budget', 0), data.get('insurance_deductibles', 0)
        ))
        client_id = cursor.lastrowid
        
        for acc in data.get('accounts', []):
            cursor.execute('''
                INSERT INTO accounts (client_id, institution, acc_type, last4, category, owner, last_known_balance, interest_rate, cash_balance, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client_id, acc.get('institution'), acc.get('acc_type'), acc.get('last4'), acc.get('category'), acc.get('owner'),
                acc.get('last_known_balance', 0), acc.get('interest_rate', 0), acc.get('cash_balance', 0), acc.get('address', '')
            ))
        conn.commit()
        return client_id

def update_client(client_id, data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clients SET 
                is_joint=?, name=?, dob=?, ssn_last4=?, salary_client1=?, spouse_name=?, spouse_dob=?, spouse_ssn_last4=?, 
                salary_client2=?, expense_budget=?, insurance_deductibles=?
            WHERE id=?
        ''', (
            data.get('is_joint', False), data.get('name'), data.get('dob'), data.get('ssn_last4'), data.get('salary_client1', 0),
            data.get('spouse_name'), data.get('spouse_dob'), data.get('spouse_ssn_last4'), data.get('salary_client2', 0),
            data.get('expense_budget', 0), data.get('insurance_deductibles', 0),
            client_id
        ))
        
        cursor.execute('DELETE FROM accounts WHERE client_id=?', (client_id,))
        for acc in data.get('accounts', []):
            cursor.execute('''
                INSERT INTO accounts (client_id, institution, acc_type, last4, category, owner, last_known_balance, interest_rate, cash_balance, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client_id, acc.get('institution'), acc.get('acc_type'), acc.get('last4'), acc.get('category'), acc.get('owner'),
                acc.get('last_known_balance', 0), acc.get('interest_rate', 0), acc.get('cash_balance', 0), acc.get('address', '')
            ))
        conn.commit()

def get_clients():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients')
        return [dict(row) for row in cursor.fetchall()]

def get_client(client_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE id=?', (client_id,))
        client = cursor.fetchone()
        if not client:
            return None
        
        client_dict = dict(client)
        cursor.execute('SELECT * FROM accounts WHERE client_id=?', (client_id,))
        client_dict['accounts'] = [dict(row) for row in cursor.fetchall()]
        return client_dict

def update_account_balances(client_id, account_updates):
    with get_db() as conn:
        cursor = conn.cursor()
        for update in account_updates:
            cursor.execute('''
                UPDATE accounts 
                SET last_known_balance=?, cash_balance=? 
                WHERE id=? AND client_id=?
            ''', (update.get('balance', 0), update.get('cash_balance', 0), update.get('id'), client_id))
        conn.commit()

def save_report(client_id, date, data):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reports (client_id, date, data)
            VALUES (?, ?, ?)
        ''', (client_id, date, json.dumps(data)))
        return cursor.lastrowid

if __name__ == "__main__":
    init_db()
