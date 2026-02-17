import os
import psycopg
import datetime

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "AttendanceSystem")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

class DB:
    conn = psycopg.connect(f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} connect_timeout=10")

    @staticmethod
    def students():
        with DB.conn.cursor() as cur:
            return cur.execute("SELECT * FROM public.students").fetchall()

    @staticmethod
    def student(student_id):
        with DB.conn.cursor() as cur:
            return cur.execute("SELECT * FROM public.students WHERE id = %s", (student_id)).fetchone()
        
    @staticmethod
    def insert_student(student_number, full_name, student_email):
        with DB.conn.cursor() as cur:
            return cur.execute(
                "INSERT INTO public.students (student_number, full_name, student_email) VALUES (%s, %s, %s)",
                (student_number, full_name, student_email))
    

    @staticmethod
    def attendance_logs():
        with DB.conn.cursor() as cur:
            return cur.execute("SELECT * FROM public.attendance_logs").fetchall()
        
    @staticmethod
    def insert_attendance_log(student_id):
        time_now = datetime.datetime.now()

        with DB.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.attendance_logs (student_id, created_at) VALUES (%s, %s)",
                (student_id, time_now)) 