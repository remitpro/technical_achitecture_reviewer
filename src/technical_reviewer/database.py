import sqlite3
import os
from datetime import datetime

DB_PATH = "jobs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            file_path TEXT NOT NULL,
            output_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_job(job_id: str, status: str, file_path: str, output_name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute('''
        INSERT INTO jobs (job_id, status, file_path, output_name, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (job_id, status, file_path, output_name, now, now))
    conn.commit()
    conn.close()

def update_job_status(job_id: str, status: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute('''
        UPDATE jobs
        SET status = ?, updated_at = ?
        WHERE job_id = ?
    ''', (status, now, job_id))
    conn.commit()
    conn.close()

def get_job(job_id: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT job_id, status, file_path, output_name, created_at, updated_at FROM jobs WHERE job_id = ?', (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "job_id": row[0],
            "status": row[1],
            "file_path": row[2],
            "output_name": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        }
    return None
