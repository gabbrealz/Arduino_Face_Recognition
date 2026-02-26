from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from deepface import DeepFace
from db import DB


if __name__ == "__main__":
    students = [
        DB.insert_student("Christian Gabriel Agot", "christian@college.com"),
        DB.insert_student("June Benedict Malabanan", "june@college.com"),
        DB.insert_student("Roycee Hugh Lacuesta", "roycee@college.com"),
        DB.insert_student("Lourd Marcus de Leon", "lourd@college.com")
    ]

    test_images_directory = Path(__file__).parent.parent.parent/"test"/"data"

    embedding1 = DeepFace.represent(test_images_directory/"gabb1.jpg", model_name="ArcFace")[0]["embedding"]
    embedding2 = DeepFace.represent(test_images_directory/"june.jpg", model_name="ArcFace")[0]["embedding"]
    embedding2 = DeepFace.represent(test_images_directory/"roycee.jpg", model_name="ArcFace")[0]["embedding"]

    DB.register_face(students[0], embedding1)
    DB.register_face(students[1], embedding2)
    DB.register_face(students[2], embedding2)