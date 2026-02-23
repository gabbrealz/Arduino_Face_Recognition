import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import CameraApp from "./components/CameraApp";
import PopupOverlay from "./components/PopupOverlay";
import './App.css';

export default function App() {
  const [capturedImage, setCapturedImage] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleCapture = (imageDataUrl) => {
    if (isLoading) return;

    setIsLoading(true);
    
    setTimeout(() => {
      setCapturedImage(imageDataUrl);
      setShowPopup(true);
      setIsLoading(false);
    }, 200); 
  };

  const handleClose = () => {
    setShowPopup(false);
    setTimeout(() => setCapturedImage(null), 100);
  };

  return (
    <BrowserRouter>
      <div className="app-layout">
        <main className="main-viewport">
          {isLoading && (
            <div className="loading-overlay">
              <div className="pulse-loader"></div>
              <p>Processing...</p>
            </div>
          )}

          <Routes>
            <Route 
              path="/" 
              element={<CameraApp onCapture={handleCapture} />} 
            />
          </Routes>
        </main>

        {showPopup && capturedImage && (
          <PopupOverlay
            image={capturedImage}
            onClose={handleClose}
          />
        )}
      </div>
    </BrowserRouter>
  );
}