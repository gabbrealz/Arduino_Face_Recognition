export default function CameraApp({ streamImage, forRegistration }) {
  return (
    <div className="camera-app">
      <h2 style={{ margin: "16px", textAlign: "center" }}>
        {forRegistration ? "Register Student" : "Log Attendance"}
      </h2>
      <div className="viewfinder">
        {streamImage ? (
          <img 
            src={streamImage} 
            alt="Live Stream" 
            style={{ 
              width: "100%", 
              height: "100%", 
              objectFit: "cover",
              display: "block" // Removes bottom whitespace
            }} 
          />
        ) : (
          <div className="placeholder">Waiting for stream...</div>
        )}
      </div>
    </div>
  );
}