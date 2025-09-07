#!/usr/bin/env python3
"""
Script para inicializar la base de datos de Loginexia
"""

import os
import sys
from datetime import datetime

# Añadir el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Crear base de datos SQLite
import sqlite3

def init_database():
    """Inicializar la base de datos con tablas básicas"""
    
    # Asegurar que el directorio existe
    os.makedirs('data', exist_ok=True)
    
    # Conectar a la base de datos
    conn = sqlite3.connect('data/loginexia.db')
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            role TEXT DEFAULT 'user',
            organization_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Crear tabla de organizaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            domain TEXT,
            subscription_tier TEXT DEFAULT 'basic',
            api_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Crear tabla de repartidores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS riders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            status TEXT DEFAULT 'active',
            organization_id INTEGER,
            last_location_lat REAL,
            last_location_lon REAL,
            last_seen TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    ''')
    
    # Crear tabla de alertas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rider_id INTEGER,
            type TEXT NOT NULL,
            severity TEXT DEFAULT 'medium',
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (rider_id) REFERENCES riders(id)
        )
    ''')
    
    # Crear tabla de métricas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rider_id INTEGER,
            metric_type TEXT NOT NULL,
            value REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rider_id) REFERENCES riders(id)
        )
    ''')
    
    # Crear usuario demo
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, password_hash, name, role, organization_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        'demo@loginexia.com',
        'pbkdf2:sha256:600000$demo$demo',  # Password: demo123
        'Usuario Demo',
        'admin',
        1
    ))
    
    # Crear organización demo
    cursor.execute('''
        INSERT OR IGNORE INTO organizations (id, name, domain, subscription_tier)
        VALUES (?, ?, ?, ?)
    ''', (
        1,
        'Demo Organization',
        'loginexia.com',
        'enterprise'
    ))
    
    # Commit cambios
    conn.commit()
    
    # Verificar tablas creadas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("✅ Base de datos inicializada correctamente")
    print(f"📊 Tablas creadas: {[t[0] for t in tables]}")
    
    # Cerrar conexión
    conn.close()
    
    return True

if __name__ == "__main__":
    try:
        init_database()
        print("\n✅ Base de datos lista para usar")
        print("📧 Usuario demo: demo@loginexia.com")
        print("🔑 Password: demo123")
    except Exception as e:
        print(f"❌ Error inicializando BD: {e}")
        sys.exit(1)
