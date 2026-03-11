import { useEffect } from "react";

export default function CameraApp({ streamImage, showRegistration, setShowRegistration, isFaceDetected }) {
  useEffect(() => {
    setShowRegistration(localStorage.getItem("STUDENT_NUMBER_FROM_REGISTRATION") !== null);
  }, []);

  return (
    <div className={`camera-app ${isFaceDetected ? "face-detected-glow" : ""}`}>
      <div className="header-badge">
        {showRegistration ? "Register Student" : "Log Attendance"}
      </div>
      <div className="viewfinder">
        {streamImage ? (
          <img 
            src={streamImage} 
            alt="Live Stream" 
            style={{ 
              width: "100%", 
              height: "100%", 
              objectFit: "cover",
              display: "block" 
            }} 
          />
        ) : (
          <div className="placeholder">Waiting for stream...</div>
        )}
      </div>
    </div>
  );
}