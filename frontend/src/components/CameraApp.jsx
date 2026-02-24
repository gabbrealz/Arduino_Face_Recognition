export default function CameraApp({ streamImage, onCapture }) {
  return (
    <div className="camera-app">
      <div className="viewfinder">
        {streamImage ? (
          <img src={streamImage} alt="Live Stream" />
        ) : (
          <div className="placeholder">Waiting for stream...</div>
        )}
      </div>
    </div>
  );
}