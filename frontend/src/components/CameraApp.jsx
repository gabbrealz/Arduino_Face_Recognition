export default function CameraApp({ streamImage, onCapture }) {
  return (
    <div className="camera-app">
      <div className="viewfinder">
        {streamImage ? (
          <img src={streamImage} alt="Live Stream" />
        ) : (
          <div className="placeholder">Waiting for stream...</div>
        )}

        <div className="camera-controls">
          <button
            className="shutter-btn"
            onClick={onCapture}
            aria-label="Take Photo"
          />
        </div>
      </div>
    </div>
  );
}