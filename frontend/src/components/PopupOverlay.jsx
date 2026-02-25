import { useEffect } from "react";
import AttendanceCard from "./AttendanceCard";

export default function PopupOverlay({ image, onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000);

    return () => {
      clearTimeout(timer);
    };
  }, [onClose]);

  const safeResult = result ? result.trim() : "";
  const isError = safeResult === "no student detected" || safeResult === "invalid image";

  return (
    <div
      className="popup-overlay"
      onClick={(e) => {
        if (e.target.classList.contains("popup-overlay")) {
          onClose();
        }
      }}
    >
      {isError ? (
        <div
          className="error-card"
          style={{
            background: 'white',
            padding: '30px',
            borderRadius: '12px',
            textAlign: 'center',
            color: '#d9534f',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            maxWidth: '300px',
            margin: '0 auto',
          }}
        >
          <h2 style={{ margin: '0 0 10px 0' }}>Recognition Failed</h2>
          <p style={{ fontSize: '16px', color: '#333' }}>
            {safeResult === "no student detected"
              ? "No student detected in the image."
            : "Invalid image. Please try again."}
          </p>
        </div>
      ) : (
        <AttendanceCard image={image} studentData={safeResult} />
      )}
      </div>
  );
}