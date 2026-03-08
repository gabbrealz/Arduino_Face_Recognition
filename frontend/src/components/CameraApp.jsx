export default function CameraApp({ streamImage, forRegistration }) {

  return (
    <div className="camera-app">
      <div className="header-badge">
        {forRegistration ? "Register Student" : "Log Attendance"}
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