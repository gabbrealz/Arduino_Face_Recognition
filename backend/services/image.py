from deepface import DeepFace
import asyncio
import numpy as np
import cv2

class Image:
    @staticmethod
    def get_decoded_img(img_bytes, rotate=False):
        frame = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return frame if not rotate else cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    @staticmethod
    async def get_embedding(img):
        result = await asyncio.to_thread(DeepFace.represent, img, model_name="ArcFace", enforce_detection=True)
        if (len(result) == 0 or len(result) > 1):
            raise ValueError()

        return result[0]["embedding"]