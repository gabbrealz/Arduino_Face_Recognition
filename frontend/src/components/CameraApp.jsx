import { useEffect, useRef, useCallback, useState } from "react";

export default function CameraApp({ onCapture }) {
  const videoRef = useRef(null);
  const [photoPreview, setPhotoPreview] = useState(null);

  const handleCapture = useCallback(() => {
    if (videoRef.current) {
      const video = videoRef.current;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");

      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const dataUrl = canvas.toDataURL("image/png");
      
      setPhotoPreview(dataUrl); 
      onCapture(dataUrl);       
    }
  }, [onCapture]);

  useEffect(() => {
    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" },
          audio: false,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Camera access denied:", err);
      }
    };

    const handleKeyDown = (event) => {
      if (event.target.tagName !== "INPUT" && (event.code === "Space" || event.key === " ")) {
        event.preventDefault();
        handleCapture();
      }
    };

    initCamera();
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleCapture]);

  return (
    <div className="camera-app">
      <div className="viewfinder">
        <video ref={videoRef} id="video" autoPlay playsInline />
        
        <div className="camera-controls">
          <button
            className="shutter-btn"
            id="toggle-popup-btn"
            onClick={handleCapture}
            aria-label="Take Photo"
          />
        </div>
      </div>
    </div>
  );
}