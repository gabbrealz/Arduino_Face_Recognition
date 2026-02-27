import { useState, useEffect, useRef, useCallback, useContext } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import mqtt from "mqtt";
import Notifications from "./components/Notifications";
import CameraApp from "./components/CameraApp";
import PopupOverlay from "./components/PopupOverlay";
import AdminHomepage from "./pages/AdminHomepage";
import { NotifContext, RegistrationContext } from "./Contexts";
import './App.css';

export default function App() {
  const { addToNotifs } = useContext(NotifContext);
  const { registrationData, setRegistrationData } = useContext(RegistrationContext);
  
  const [capturedImage, setCapturedImage] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [streamImage, setStreamImage] = useState(null);
  const [recognitionResult, setRecognitionResult] = useState(null);

  const wsRef = useRef(null);
  const mqttRef = useRef(null);

  const isLoadingRef = useRef(isLoading);
  const registrationDataRef = useRef(registrationData);
  const streamImageRef = useRef(streamImage);

  useEffect(() => {
    isLoadingRef.current = isLoading;
  }, [isLoading]);

  useEffect(() => {
    registrationDataRef.current = registrationData;
  }, [registrationData]);


  useEffect(() => {
    const socket = new WebSocket("ws://10.139.37.34:8000/camera");
    socket.binaryType = "arraybuffer";

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
      if (event.data instanceof Blob || event.data instanceof ArrayBuffer) {
        if (isLoadingRef.current) return;
        
        const blob = event.data instanceof Blob ? event.data : new Blob([event.data], { type: "image/jpeg" });

        const imageUrl = URL.createObjectURL(blob);
        streamImageRef.current = imageUrl;
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


  const registerFace = async () => {
    setIsLoading(true);

    try {
      const responseFromUrl = await fetch(streamImageRef.current);
      const imageBlob = await responseFromUrl.blob();

      const response = await fetch(`http://localhost:8000/students/${registrationDataRef.current.studentNumber}/register-face`, {
        method: "POST",
        headers: {
          "Content-Type": "image/jpeg",
        },
        body: imageBlob
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to register face");
      }

      addToNotifs({
        bgColor: "#008000",
        message: "Successfully registered student!"
      })
      setRegistrationData({ forRegistration: false });

      mqttRef.current.publish("arduino-r4/input", JSON.stringify({
        req: "RGSTR",
        msg: "Student added!",
        success: true,
      }), { qos: 2 }, (err) => { if (err) console.error("Publish error:", err); });
    }
    catch (error) {
      console.error(error);
      addToNotifs({
        bgColor: "#992020",
        message: error.message
      });
      mqttRef.current.publish("arduino-r4/input", JSON.stringify({
        req: "RGSTR",
        msg: "Failed to add!",
        success: false,
      }), { qos: 2 }, (err) => { if (err) console.error("Publish error:", err); });
    }
    finally {
      setIsLoading(false);
    }
  };


  useEffect(() => {
    const mqttClient = mqtt.connect("ws://10.139.37.34:9001", {
      clientId: "vite-frontend",
      will: {
        topic: "fastapi/capture/mode",
        payload: "ATTND",
        qos: 2
      }
    });
    
    mqttClient.on("connect", () => {
      console.log("MQTT connected");

      mqttClient.subscribe("arduino-r4/output", { qos: 2 }, (err) => {
        if (err) console.error("Subscribe error:", err);
      });

      mqttClient.subscribe("frontend/attendance-log/response", { qos: 2 }, (err) => {
        if (err) console.error("Subscribe error:", err);
      });

      if (registrationDataRef.current.forRegistration) {
        mqttClient.publish("fastapi/capture/mode", "RGSTR", { qos: 2 }, (err) => {
          if (err) console.error("Publish error:", err);
        });
      }
      else {
        mqttClient.publish("fastapi/capture/mode", "ATTND", { qos: 2 }, (err) => {
          if (err) console.error("Publish error:", err);
        });
      }

    });

    mqttClient.on("message", (topic, message) => {
      const messageStr = new TextDecoder().decode(message);
      console.log(messageStr);

      if (topic === "arduino-r4/output") {
        setCapturedImage(streamImage);
        setIsLoading(true);

        if (registrationDataRef.current.forRegistration)
          registerFace();
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
      <Notifications/>
      <div className="app-layout">
        <main className="main-viewport">
          {isLoading && (
            <div className="loading-overlay">
              <div className="pulse-loader"></div>
              <p>Processing...</p>
            </div>
          )}

          <Routes>
            <Route path="/" element={<CameraApp streamImage={streamImage} forRegistration={registrationDataRef.current.forRegistration} />} />
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