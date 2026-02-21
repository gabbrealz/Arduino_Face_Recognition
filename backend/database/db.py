import os
import psycopg
from datetime import datetime

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
DB_NAME = os.getenv("POSTGRES_DB", "AttendanceSystem")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

class DB:
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    @staticmethod
    def reconnect():
        DB.conn.close()
        DB.conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

    
    @staticmethod
    def get_matching_face(embedding, threshold):
        with DB.conn.cursor() as cur:
            return cur.execute("SELECT get_matching_face(%s, %s)", (embedding, threshold)).fetchone()


    @staticmethod
    def students():
        with DB.conn.cursor() as cur:
            return cur.execute("SELECT id, student_number, full_name, student_email FROM public.students").fetchall()

    @staticmethod
    def student(student_id):
        with DB.conn.cursor() as cur:
            return cur.execute(
                "SELECT id, student_number, full_name, student_email FROM public.students WHERE id = %s LIMIT 1", 
                (student_id)).fetchone()

    @staticmethod
    def insert_student(student_number, full_name, student_email):
        with DB.conn.cursor() as cur:
            return cur.execute(
                "INSERT INTO public.students (student_number, full_name, student_email) VALUES (%s, %s, %s)",
                (student_number, full_name, student_email))
    

    @staticmethod
    def attendance_logs():
        with DB.conn.cursor() as cur:
            return cur.execute("""
                SELECT l.created_at, s.student_number, s.full_name, s.student_email
                FROM public.attendance_logs l
                JOIN public.students s ON l.student_id = s.id
            """).fetchall()
        
    @staticmethod
    def insert_attendance_log(student_id):
        with DB.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.attendance_logs (student_id, created_at) VALUES (%s, %s)",
                (student_id, datetime.now()))


    @staticmethod
    def face_embeddings():
        with DB.conn.cursor() as cur:
            return cur.execute("SELECT * FROM public.face_embeddings").fetchall()

    @staticmethod
    def insert_face_embedding(student_id, embedding):
        with DB.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.face_embeddings (student_id, embedding) VALUES (%s, %s)",
                (student_id, embedding))