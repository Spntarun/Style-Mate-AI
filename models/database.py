import sqlite3
import hashlib
import os
from flask import g

def get_db(app):
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db(app):
    with app.app_context():
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        
        # Users table
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                height REAL,
                weight REAL,
                chest REAL,
                waist REAL,
                hips REAL,
                body_type TEXT,
                skin_tone TEXT,
                gender TEXT,
                profile_image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vendors table
        db.execute('''
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                brand_name TEXT,
                phone TEXT,
                address TEXT,
                logo TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                gender TEXT,
                price REAL,
                size TEXT,
                color TEXT,
                occasion TEXT,
                climate TEXT,
                body_type TEXT,
                skin_tone TEXT,
                image TEXT,
                stock INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES vendors(id)
            )
        ''')
        
        # Orders table
        db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                vendor_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                total_price REAL,
                status TEXT DEFAULT 'pending',
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id)
            )
        ''')
        
        # AI Generated Outfits table
        db.execute('''
            CREATE TABLE IF NOT EXISTS generated_outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                prompt TEXT,
                generated_image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Admin table
        db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default admin
        try:
            db.execute('''
                INSERT INTO admins (name, email, password)
                VALUES (?, ?, ?)
            ''', ('Admin', 'admin@StyleMate.com', hash_password('admin123')))
        except:
            pass
        
        # Insert sample vendors (approved)
        try:
            db.execute('''
                INSERT INTO vendors (name, email, password, brand_name, phone, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('Vendor One', 'vendor@StyleMate.com', hash_password('vendor123'), 'StyleHub', '9876543210', 'approved'))
        except:
            pass
        
        db.commit()
        db.close()
