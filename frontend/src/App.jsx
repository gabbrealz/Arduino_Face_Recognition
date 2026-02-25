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
  const mqttRef = useRef(null);

  const isLoadingRef = useRef(isLoading);

  useEffect(() => {
    isLoadingRef.current = isLoading;
  }, [isLoading]);

  useEffect(() => {
    const socket = new WebSocket("ws://192.168.1.168:8000/camera");
    socket.binaryType = "arraybuffer";

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
      if (event.data instanceof Blob || event.data instanceof ArrayBuffer) {
        if (isLoading) return;
        
        const blob = event.data instanceof Blob ? event.data : new Blob([event.data], { type: "image/jpeg" });

        const imageUrl = URL.createObjectURL(blob);
        setStreamImage((prev) => {
          if (prev) URL.revokeObjectURL(prev); 
          return imageUrl;
        });
      }
      else {
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
    const mqttClient = mqtt.connect("ws://192.168.1.168:9001");
    
    mqttClient.on("connect", () => {
      console.log("MQTT connected");

      mqttClient.subscribe("arduino-r4/output", { qos: 2 }, (err) => {
        if (err) console.error("Subscribe error:", err);
      });

      mqttClient.subscribe("frontend/attendance-log/response", { qos: 2 }, (err) => {
        if (err) console.error("Subscribe error:", err);
      });

    });

    mqttClient.on("message", (topic, message) => {
      const messageStr = new TextDecoder().decode(message);
      console.log(messageStr);

      if (topic === "arduino-r4/output") {
        setCapturedImage(streamImage);
        setIsLoading(true);
      }
      else if (topic === "frontend/attendance-log/response") {
        const data = JSON.parse(messageStr);
        setIsLoading(false);
        setRecognitionResult(data);
        setShowPopup(true);
      }
    });

    mqttRef.current = mqttClient;

    return () => {
      if (mqttClient) mqttClient.end();
    };
  }, []);

  useEffect(() => {
    if (isLoading && streamImage) {
      setCapturedImage(streamImage);
    }
  }, [streamImage, isLoading]);


  const handleClose = useCallback(() => {
    setShowPopup(false);
    setTimeout(() => {
      setCapturedImage(null);
      setRecognitionResult(null);
    }, 100);
  }, []);

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
            <Route path="/" element={<CameraApp streamImage={streamImage} />} />
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