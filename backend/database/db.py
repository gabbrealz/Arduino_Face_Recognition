import os
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "AttendanceSystem")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

class DB:
    dsn = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    pool = ConnectionPool(conninfo=dsn, kwargs={"row_factory": dict_row})

    @staticmethod
    def log_attendance_for_face(embedding, threshold):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM log_attendance_for_face(%s, %s)", (embedding, threshold))
                return cur.fetchone()

    @staticmethod
    def register_face(embedding):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT register_face(%s)", (embedding,))
                return cur.fetchone()["register_face"]


    @staticmethod
    def get_students():
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, student_number, full_name, student_email FROM public.students")
                return cur.fetchall()

    @staticmethod
    def get_student(student_id):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, student_number, full_name, student_email FROM public.students WHERE id = %s LIMIT 1", 
                    (student_id,))
                return cur.fetchone()

    @staticmethod
    def insert_student(student_number, full_name, student_email):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.students (student_number, full_name, student_email) VALUES (%s, %s, %s)",
                    (student_number, full_name, student_email))
    

    @staticmethod
    def get_attendance_logs():
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT l.created_at, s.student_number, s.full_name, s.student_email
                    FROM public.attendance_logs l
                    JOIN public.students s ON l.student_id = s.id
                """)
                return cur.fetchall()
        
    @staticmethod
    def insert_attendance_log(student_id):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.attendance_logs (student_id) VALUES (%s)",
                    (student_id,))