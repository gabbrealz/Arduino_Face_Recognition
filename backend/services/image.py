from deepface import DeepFace
import asyncio
import numpy as np
import cv2

class Image:
    @staticmethod
    def get_decoded_img(img_bytes):
        img_nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(img_nparr, cv2.IMREAD_COLOR)

    @staticmethod
    async def get_embedding(img):
        result = await asyncio.to_thread(DeepFace.represent, img, model_name="ArcFace")
        return result[0]["embedding"]

class Face:
    @staticmethod
    async def image_is_valid(img):
        try:
            faces = await asyncio.to_thread(
                DeepFace.extract_faces,
                img_path=img,
                detector_backend="opencv",
                enforce_detection=True,
                anti_spoofing=True
            )
            return any(face.get("is_real", False) for face in faces)

        except ValueError:
            return False