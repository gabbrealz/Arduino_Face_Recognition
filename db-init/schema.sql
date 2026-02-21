CREATE EXTENSION vector;

CREATE TABLE public.students (
    id BIGSERIAL,
    student_number CHAR(12) NOT NULL,
    full_name TEXT NOT NULL,
    student_email TEXT NOT NULL,

    CONSTRAINT students_pkey PRIMARY KEY (id),
    CONSTRAINT student_number_pattern CHECK (student_number ~ '\d{4}-\d{3}-\d{3}'),
    CONSTRAINT unique_email UNIQUE (email),
    CONSTRAINT email_pattern CHECK (email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')
);

CREATE TABLE public.face_embeddings (
    id BIGSERIAL,
    embedding VECTOR(512) NOT NULL,
    student_id BIGINT,

    CONSTRAINT face_embeddings_pkey PRIMARY KEY (id),
    CONSTRAINT face_to_student_fkey FOREIGN KEY (student_id)
    REFERENCES public.students(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE public.attendance_logs (
    id BIGSERIAL,
    student_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT attendance_logs_pkey PRIMARY KEY (id),
    CONSTRAINT attendance_log_to_student_fkey FOREIGN KEY (student_id)
    REFERENCES public.students(id)
    ON UPDATE CASCADE
    ON DELETE NO ACTION
);


CREATE OR REPLACE FUNCTION get_matching_face(embedding VECTOR(512))
RETURNS TABLE(id BIGINT, student_number CHAR(12), full_name TEXT, student_email TEXT) AS $$
DECLARE
    p_student_id BIGINT
BEGIN
    SELECT f.student_id INTO p_student_id
    FROM public.face_embeddings f
    ORDER BY f.embedding <=> embedding
    LIMIT 1;

    RETURN QUERY
    SELECT s.id, s.student_number, s.full_name, s.student_email
    FROM public.students
    WHERE s.id = p_student_id;
END;
$$ LANGUAGE plpgsql;