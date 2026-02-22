CREATE EXTENSION vector;


CREATE TABLE public.students (
    id BIGSERIAL,
    student_number CHAR(12) NOT NULL,
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