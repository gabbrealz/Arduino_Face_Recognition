import os
from psycopg_pool import ConnectionPool

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "AttendanceSystem")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

class DB:
    pool = ConnectionPool(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

    @staticmethod
    def log_attendance_for_face(embedding, threshold):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                return cur.execute("SELECT log_attendance_for_face(%s, %s)", (embedding, threshold)).fetchone()


    @staticmethod
    def get_students():
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                return cur.execute("SELECT id, student_number, full_name, student_email FROM public.students").fetchall()

    @staticmethod
    def get_student(student_id):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                return cur.execute(
                    "SELECT id, student_number, full_name, student_email FROM public.students WHERE id = %s LIMIT 1", 
                    (student_id)).fetchone()

    @staticmethod
    def insert_student(student_number, full_name, student_email):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                return cur.execute(
                    "INSERT INTO public.students (student_number, full_name, student_email) VALUES (%s, %s, %s)",
                    (student_number, full_name, student_email))
    

    @staticmethod
    def get_attendance_logs():
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                return cur.execute("""
                    SELECT l.created_at, s.student_number, s.full_name, s.student_email
                    FROM public.attendance_logs l
                    JOIN public.students s ON l.student_id = s.id
                """).fetchall()
        
    @staticmethod
    def insert_attendance_log(student_id):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.attendance_logs (student_id) VALUES (%s)",
                    (student_id))


    @staticmethod
    def get_face_embeddings():
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                return cur.execute("SELECT * FROM public.face_embeddings").fetchall()

    @staticmethod
    def insert_face_embedding(student_id, embedding):
        with DB.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.face_embeddings (student_id, embedding) VALUES (%s, %s)",
                    (student_id, embedding))