# **Django WebSockets Project**

## Overview
This is a **full-stack Django and React application** that implements:

- **WhatsApp-like chat** with WebSockets.
- **YouTube-like video upload & playback** with **FFmpeg compression**.
- **Real-time progress updates** using **Django Channels** and **WebSockets**.

---

## Features
### 🔹 **WhatsApp-Like Chat**
- **Real-time messaging** using WebSockets.
- **One-on-one and group chats**.
- **Message status updates** (*sent, delivered, read*).
- **Online/offline user status**.

### 🔹 **YouTube-Like Video Upload & Playback**
- **Video uploads** using Django REST API.
- **Real-time upload progress** via WebSockets.
- **FFmpeg compression** for optimized video storage.
- **Video duration retrieval before upload**.
- **Streaming video playback** using React Player.

---

## 🛠 Tech Stack
### **Backend (Django)**
-  **Django** – Web framework.
-  **Django Channels** – WebSockets support.
-  **Celery** – Background video processing.
-  **Redis** – Message broker for Celery.
-  **FFmpeg** – Video compression.

### **Frontend (React)**
- **React** – UI framework.
- **react-player** – Video player.
- **WebSockets API** – Real-time updates.

---

## Installation & Setup
### 🔹 **Clone the Repository**
```sh
git clone https://github.com/MohammadOwais655/youtube-backend.git
cd youtube-backend
```

### 🔹 **Backend Setup (Django)**
1️⃣ **Create a virtual environment:**
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2️⃣ **Install dependencies:**
```sh
pip install -r requirements.txt
```

3️⃣ **Run migrations:**
```sh
python manage.py makemigrations
python manage.py migrate
```

4️⃣ **Start the Django server:**
```sh
python manage.py runserver
```
```sh
celery -A backend worker --loglever=info
```

### 🔹 **Frontend Setup (React)**
```sh
git clone https://github.com/MohammadOwais655/youtube-frontend.git
cd frontend
npm install
npm start
```

---

## 🔗 WebSocket Implementation
### 🔹 **Chat WebSocket Endpoint**
```sh
ws://localhost:8000/ws/chat/?receiverId=${receiverId}&token=${token}
```

---

## API Endpoints
### 🔹 **Authentication**
```http
POST /api/v1/users/create-user
POST /api/v1/users/authenticate
POST /api/v1/users/logout
POST /api/v1/users/reset-password
```

### 🔹 **Video API**
```http
POST /api/v1/videos/upload-video  # Upload a video
GET /api/v1/videos/get-video/<int:videoId>  # Single video
PUT /api/v1/videos/update-video/<int:videoId>  # Update video
DELETE /api/v1/videos/delete-video/<int:videoId>  # Delete video
GET /api/video/all-videos/  # Get uploaded videos
```

---

## Contributing
Feel free to **submit issues and pull requests**!

---

## License
**MIT License**

