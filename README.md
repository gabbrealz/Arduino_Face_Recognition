# 🎯 Arduino Face Recognition System

A distributed **IoT-based Face Recognition System** integrating embedded hardware, backend processing, real-time messaging (MQTT + WebSocket), and a web-based dashboard.

This project combines microcontroller-based image acquisition with server-side facial recognition to provide real-time identification, logging, and physical feedback.

---

# Table of Contents

* [Overview](#-overview)
* [System Architecture](#-system-architecture)
* [Hardware Components](#-hardware-components)
* [Backend](#-backend)
* [Frontend](#-frontend)
* [Installation](#-installation)
* [System Workflow](#-system-workflow)
* [Deployment](#-deployment)
* [Future Improvements](#-future-improvements)
* [License](#-license)

---

# Overview

The system consists of three major layers:

* **Hardware Layer** – Captures facial images and controls physical indicators
* **Backend Layer** – Performs face recognition and system logic
* **Frontend Layer** – Displays real-time dashboard and logs

Real-time communication is achieved using:

* **MQTT** → IoT publish–subscribe messaging
* **WebSocket** → Live frontend updates

---

# 🏗 System Architecture

```
ESP32-CAM → Backend Server → Database
       ↓            ↓
   Arduino      MQTT Broker
       ↓            ↓
  LEDs / LCD   WebSocket → Frontend Dashboard
```

---

# 🔧 Hardware Components

* 1x Arduino Uno R4 WiFi
* 1x ESP32-CAM
* 1x 16x2 LCD with I2C
* 1x Push Button
* 2x LED Lights (Green & Red)
* 1x Piezo Buzzer

### 🔹 Hardware Function

* **ESP32-CAM** captures facial images and sends them to the backend.
* **Arduino Uno R4 WiFi** controls LCD, LEDs, and buzzer.
* **LCD** displays recognition status.
* **Green LED** → Authorized
* **Red LED** → Unauthorized
* **Piezo** → Audio feedback

---

# Backend

### Responsibilities

* Receive image data from ESP32-CAM
* Perform facial recognition
* Store user encodings & logs
* Publish events via MQTT
* Send live updates via WebSocket
* Provide REST API for frontend

### Technologies

* Face recognition library
* WebSocket server
* MQTT client
* Database
* Docker container

---

# Frontend

### Responsibilities

* Real-time recognition dashboard
* User registration & management
* Recognition logs viewer
* REST API integration
* WebSocket live updates

---

# Installation

## 1️ Clone Repository

```bash
git clone https://github.com/gabbrealz/Arduino_Face_Recognition.git
cd Arduino_Face_Recognition
```

---

## 2️ Hardware Setup

* Connect ESP32-CAM and Arduino components
* Ensure stable 5V power supply
* Verify TX/RX voltage levels
* Upload firmware using Arduino IDE

---

## 3️ Backend Setup

### Option A: Docker (Recommended)

Install:

* Docker
* Docker Compose

Run:

```bash
docker-compose up --build
```

---

### Option B: Manual Setup

```bash
cd backend
npm install
npm start
```

(or use `pip install -r requirements.txt` if Python-based)

---

## 4️ Database Initialization

Run initialization scripts inside:

```
/db-init
```

Ensure backend successfully connects to database.

---

## 5️ MQTT Broker Setup

Install broker such as Eclipse Mosquitto.

Verify topic communication before starting backend.

---

## 6️ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open:

```
http://localhost:<port>
```

---

# System Workflow

1. Camera captures face
2. Image sent to backend
3. Backend performs recognition
4. Result stored in database
5. Event published via MQTT
6. Frontend updated via WebSocket
7. Arduino triggers LEDs, LCD, and buzzer

---

# Deployment

The system supports full containerized deployment using:

* Backend container
* Frontend container
* MQTT broker
* Database service

All orchestrated via `docker-compose`.

---

# Features

* ✅ Real-time face recognition
* ✅ IoT messaging (MQTT)
* ✅ Live dashboard (WebSocket)
* ✅ Dockerized deployment
* ✅ Modular architecture
* ✅ Database logging

---

# Future Improvements

* HTTPS & Secure WebSocket (WSS)
* Role-based authentication
* Cloud deployment support
* Model retraining pipeline
* Performance optimization