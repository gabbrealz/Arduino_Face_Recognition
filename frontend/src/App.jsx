import { useState, useEffect, useRef, useCallback } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import mqtt from "mqtt";
import CameraApp from "./components/CameraApp";
import PopupOverlay from "./components/PopupOverlay";
import AdminHomepage from "./pages/AdminHomepage";
import './App.css';
export default function App() {
  const [capturedImage, setCapturedImage] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [streamImage, setStreamImage] = useState(null);
  const [recognitionResult, setRecognitionResult] = useState(null);

  const wsRef = useRef(null);

  // 🔌 Initialize WebSocket
  useEffect(() => {
    const socket = new WebSocket("ws://192.168.1.168:8000/ws");
    socket.binaryType = "arraybuffer";

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
      if (event.data instanceof Blob || event.data instanceof ArrayBuffer) {
        const blob =
          event.data instanceof Blob
            ? event.data
            : new Blob([event.data], { type: "image/jpeg" });

        const imageUrl = URL.createObjectURL(blob);
        setStreamImage((prev) => {
          if (prev) URL.revokeObjectURL(prev); 
          return imageUrl;
        });
      } else {
        console.log("Text message:", event.data);
      }
    };

    socket.onerror = (err) => console.error("WebSocket error:", err);
    socket.onclose = () => console.log("WebSocket closed");

    wsRef.current = socket;

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    const mqttClient = mqtt.connect("mqtt://ikaw na bahala gabb");
    
    mqttClient.on("connect", () => {
      console.log("MQTT connected");
      mqttClient.subscribe("ikaw na bahala gabb");
    });

    mqttClient.on("message", (topic, message) => {
      const payload = message.toString();
      console.log('MQTT Received: [${topic}]:', payload);
      setRecognitionResult(payload);

      setIsLoading(false);
      setShowPopup(true);
    });

    return () => {
      if (mqttClient) mqttClient.end();
    };
  }, []);

  // 📸 Capture current frame
  const handleCapture = useCallback(() => {
    if (isLoading || !streamImage) return;

    setCapturedImage(streamImage);
    setIsLoading(true);
  }, [isLoading, streamImage]);

  const handleClose = () => {
    setShowPopup(false);
    setTimeout(() => {
      setCapturedImage(null);
      setRecognitionResult(null);
    }, 100);
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
            <Route path="/" element={<CameraApp onCapture={handleCapture} />} />
            <Route path="/admin" element={<AdminHomepage />} />
          </Routes>
        </main>

        {showPopup && capturedImage && (
          <PopupOverlay
            image={capturedImage}
            result={recognitionResult}
            onClose={handleClose}
          />
        )}
      </div>
    </BrowserRouter>
  );
}