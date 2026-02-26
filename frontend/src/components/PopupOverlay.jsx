import { useEffect } from "react";
import AttendanceCard from "./AttendanceCard";

export default function PopupOverlay({ image, result, onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  
  return (
    <div
      className="popup-overlay"
      onClick={(e) => {
        if (e.target.classList.contains("popup-overlay")) {
          onClose();
        }
      }}
    >
      {!result.success ? (
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
            {result.msg}
          </p>
        </div>
      ) : (
        <AttendanceCard image={image} studentName={result.student.full_name} />
      )}
      </div>
  );
}