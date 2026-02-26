export default function CameraApp({ streamImage }) {
  return (
    <div className="camera-app">
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