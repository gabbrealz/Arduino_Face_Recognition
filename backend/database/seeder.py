from dotenv import load_dotenv
load_dotenv()

from db import DB

if __name__ == "__main__":
    DB.insert_student("Christian Gabriel Agot", "christian@college.com")
    DB.insert_student("June Benedict Malabanan", "june@college.com")
    DB.insert_student("Roycee Hugh Lacuesta", "roycee@college.com")
    DB.insert_student("Lourd Marcus de Leon", "lourd@college.com")