import os
import sqlite3
import random
import pandas as pd

# Absolute path configuration to eliminate terminal execution errors
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "community_resource.db")

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def initialize_database():
    """
    Initializes the database schema with normalized tables,
    enforcing primary/foreign keys and constraints.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable Foreign Key support in SQLite explicitly
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Create Community Segments Lookup Table
    cursor.execute("DROP TABLE IF EXISTS community_segments;")
    cursor.execute("""
    CREATE TABLE community_segments (
        segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        segment_name TEXT NOT NULL UNIQUE,
        description TEXT
    );
    """)
    
    # 2. Create Households Dimension/Fact Table
    cursor.execute("DROP TABLE IF EXISTS households;")
    cursor.execute("""
    CREATE TABLE households (
        household_id INTEGER PRIMARY KEY AUTOINCREMENT,
        segment_id INTEGER NOT NULL,
        household_size INTEGER NOT NULL CHECK(household_size > 0),
        monthly_water_consumption_m3 REAL, -- Intentional NULLs for Imputation Stage
        monthly_waste_generation_kg REAL,   -- Intentional NULLs for Imputation Stage
        income_index REAL CHECK(income_index >= 0.0 AND income_index <= 1.0),
        FOREIGN KEY (segment_id) REFERENCES community_segments(segment_id) 
            ON DELETE RESTRICT ON UPDATE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()
    print("[INFO] Database schemas initialized successfully with strict constraints.")

def seed_database(num_households=250, seed=42):
    """
    Seeds the database with statistically distinct populations for 
    Rural and Urban segments, incorporating missingness and anomalies.
    """
    random.seed(seed)
    conn = get_connection()
    cursor = conn.cursor()
    
    # Seed Lookups
    cursor.execute("INSERT INTO community_segments (segment_name, description) VALUES (?, ?);", 
                   ("Urban", "High-density zone, centralized utility access"))
    cursor.execute("INSERT INTO community_segments (segment_name, description) VALUES (?, ?);", 
                   ("Rural", "Low-density zone, decentralized/local resource management"))
    
    # Fetch assigned IDs
    cursor.execute("SELECT segment_id, segment_name FROM community_segments;")
    segments = {name: idx for idx, name in cursor.fetchall()}
    
    households_data = []
    
    for _ in range(num_households):
        segment = random.choice(["Urban", "Rural"])
        seg_id = segments[segment]
        
        if segment == "Urban":
            hh_size = random.randint(1, 5)
            water = random.normalvariate(18.5, 4.0) 
            waste = random.normalvariate(45.0, 10.0)
            income = min(max(random.normalvariate(0.65, 0.15), 0.0), 1.0)
        else:
            hh_size = random.randint(2, 8)
            water = random.normalvariate(12.0, 3.5)
            waste = random.normalvariate(28.0, 8.5)
            income = min(max(random.normalvariate(0.40, 0.12), 0.0), 1.0)
            
        # Introduce High-Volume Outliers (4%)
        if random.random() < 0.04:
            water *= 3.0
            waste *= 2.5
            
        # Introduce Missing Completely At Random (MCAR) Values
        water_val = None if random.random() < 0.08 else round(water, 2)
        waste_val = None if random.random() < 0.10 else round(waste, 2)
        
        households_data.append((seg_id, hh_size, water_val, waste_val, round(income, 2)))
        
    cursor.executemany("""
        INSERT INTO households (segment_id, household_size, monthly_water_consumption_m3, monthly_waste_generation_kg, income_index)
        VALUES (?, ?, ?, ?, ?);
    """, households_data)
    
    conn.commit()
    conn.close()
    print(f"[INFO] Successfully seeded database with {num_households} household records.")

def fetch_raw_pipeline_data():
    """Executes a clean relational inner join query to extract raw data."""
    conn = get_connection()
    query = """
        SELECT 
            h.household_id,
            s.segment_name,
            h.household_size,
            h.monthly_water_consumption_m3,
            h.monthly_waste_generation_kg,
            h.income_index
        FROM households h
        INNER JOIN community_segments s ON h.segment_id = s.segment_id;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    initialize_database()
    seed_database()
