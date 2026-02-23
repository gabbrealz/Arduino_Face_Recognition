import { useEffect } from "react";
import AttendanceCard from "./AttendanceCard";

export default function PopupOverlay({ image, onClose }) {
  useEffect(() => {
    // 1. Initialize and play the sound
    const audio = new Audio("/sounds/attendance.mp3");
    audio.volume = 0.5; 
    
    audio.play().catch((err) => {
      // Browsers often block sound unless the user has interacted with the page first
      console.warn("Audio playback delayed or blocked:", err);
    });

    // 2. Set the auto-close timer
    const timer = setTimeout(() => {
      onClose();
    }, 3000);

    return () => {
      clearTimeout(timer);
      // Optional: Stop the sound if the component unmounts early
      audio.pause();
      audio.currentTime = 0;
    };
  }, [onClose]);

  return (
    <div
      className="popup-overlay"
      onClick={(e) => {
        if (e.target.classList.contains("popup-overlay")) {
          onClose();
        }
      }}
    >
      <AttendanceCard image={image} />
    </div>
  );
}