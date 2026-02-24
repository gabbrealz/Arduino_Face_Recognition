CREATE EXTENSION vector;


CREATE SEQUENCE student_number_seq START 1;

CREATE OR REPLACE FUNCTION generate_student_number() RETURNS text AS $$
DECLARE seq_num INT;
BEGIN
    seq_num := nextval('student_number_seq');
    RETURN to_char(EXTRACT(YEAR FROM CURRENT_DATE), 'FM0000') || '-' ||
           to_char((seq_num / 1000)::int, 'FM000') || '-' ||
           to_char((seq_num % 1000)::int, 'FM000');
END;
$$ LANGUAGE plpgsql;

CREATE TABLE public.students (
    id BIGSERIAL,
    student_number CHAR(12) NOT NULL DEFAULT generate_student_number(),
    full_name TEXT NOT NULL,
    student_email TEXT NOT NULL,

    CONSTRAINT students_pkey PRIMARY KEY (id),
    CONSTRAINT student_number_pattern CHECK (student_number ~ '^\d{4}-\d{3}-\d{3}$'),
    CONSTRAINT unique_student_number UNIQUE (student_number),
    CONSTRAINT unique_email UNIQUE (student_email),
    CONSTRAINT email_pattern CHECK (student_email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
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
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT attendance_logs_pkey PRIMARY KEY (id),
    CONSTRAINT attendance_log_to_student_fkey FOREIGN KEY (student_id)
    REFERENCES public.students(id)
    ON UPDATE CASCADE
    ON DELETE NO ACTION
);