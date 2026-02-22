CREATE OR REPLACE FUNCTION log_attendance_for_face(p_embedding VECTOR(512), p_threshold REAL)
RETURNS TABLE(
    id BIGINT,
    student_number CHAR(12),
    full_name TEXT,
    student_email TEXT
) AS $$
DECLARE
    v_student RECORD;
BEGIN
    SELECT s.id, s.student_number, s.full_name, s.student_email INTO v_student
    FROM public.students s
    JOIN public.face_embeddings f ON f.student_id = s.id
    WHERE f.embedding <=> p_embedding < p_threshold
    ORDER BY f.embedding <=> p_embedding
    LIMIT 1;

    IF FOUND THEN
        INSERT INTO public.attendance_logs (student_id)
        VALUES (v_student.id);

        RETURN QUERY
        SELECT 
            v_student.id,
            v_student.student_number,
            v_student.full_name,
            v_student.student_email;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION register_face(p_student_number CHAR(12), p_embedding VECTOR(512))
RETURNS BOOLEAN AS $$
DECLARE
    v_student_id BIGINT;
BEGIN
    SELECT id INTO v_student_id
    FROM public.students
    WHERE student_number = p_student_number

    IF FOUND THEN
        INSERT INTO public.face_embeddings (embedding, student_id)
        VALUES (p_embedding, v_student_id);
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;