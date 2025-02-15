Django WebSockets Project

Overview

This is a full-stack Django and React application that implements:

WhatsApp-like chat with WebSockets.

YouTube-like video upload & playback with FFmpeg for compression.

Real-time progress updates using Django Channels and WebSockets.

Features

🔹 WhatsApp-Like Chat

Real-time messaging using WebSockets.

One-on-one and group chats.

Message status updates (sent, delivered, read).

Online/offline user status.

🔹 YouTube-Like Video Upload & Playback

Video uploads using Django REST API.

Real-time upload progress via WebSockets.

FFmpeg compression for optimized video storage.

Video duration retrieval before upload.

Streaming video playback using React Player.

Tech Stack

Backend (Django)

Django – Web framework.

Django Channels – WebSockets support.

Celery – Background video processing.

Redis – Message broker for Celery.

FFmpeg – Video compression.

Frontend (React)

React – UI framework.

react-player – Video player.

WebSockets API – Real-time updates.

Installation & Setup

🔹 Clone the Repository

git clone https://github.com/MohammadOwais655/youtube-backend.git
cd your-repo

🔹 Backend Setup (Django)

Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run migrations:
python manage.py makemigrations
python manage.py migrate

Start the Django server:

python manage.py runserver

🔹 Frontend Setup (React)
git clone https://github.com/MohammadOwais655/youtube-frontend.git
Navigate to the frontend directory:

cd frontend

Install dependencies:

npm install

Start the React app:

npm start

WebSocket Implementation

🔹 Chat WebSocket Endpoint

ws://localhost:8000/ws/chat/?receiverId=${receiverId}&token=${token}

API Endpoints

🔹 Authentication

POST /api/v1/users/create-user

POST /api/v1/users/authenticate

POST /api/v1/users/logout

POST /api/v1/users/reset-password

🔹 Video API

POST /api/v1/videos/upload-video – Upload a video.

GET /api/v1/videos/get-video/<int:videoId> - Single video

PUT /api/v1/videos/update-video/<int:videoId> - update video

DELETE /api/v1/videos/delete-video/<int:videoId>  - delete video

GET /api/video/all-videos/ – Get uploaded videos.

Contributing

Feel free to submit issues and pull requests!

License

MIT License

