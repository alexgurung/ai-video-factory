# 🎬 AI Video Factory (Full-Stack)

A **Human-in-the-Loop** automated video production pipeline that transforms trending tech news into high-engagement vertical shorts.

---

## 🏗️ System Architecture



```mermaid
graph TD
    subgraph Frontend [Next.js Dashboard]
        A[User: Fetch News] --> B[React State Manager]
        E[User: Edit Script] --> F[Review UI]
        H[Live Progress Bar]
        I[Video Preview Player]
    end

    subgraph Backend [FastAPI Server]
        C[HackerNews Scraper]
        D[Gemini AI Scripting]
        G[Video Pipeline Trigger]
        J[Static File Server]
    end

    subgraph Pipeline [Heavy Processing]
        K[Edge-TTS Voiceover]
        L[Pexels API Visuals]
        M[Whisper AI Transcription]
        N[MoviePy Rendering]
    end

    B <-->|REST API| C
    C --> D
    D --> F
    F -->|POST Request| G
    G --> K
    K --> L
    L --> M
    M --> N
    N -->|SSE Updates| H
    N -->|Final MP4| J
    J --> I 

```

🔬 The "Human-in-the-Loop" Design Philosophy
Fully automated AI video production often suffers from "hallucinated" facts or poor pacing. I designed this system to solve the Trust Gap in Generative AI. By inserting a human-centric review stage between script generation and final rendering, the user maintains 100% editorial control while the AI handles 90% of the manual labor.

⚡ Technical Highlights
Asynchronous Processing: Utilizes FastAPI BackgroundTasks to ensure the user interface remains responsive while the server handles heavy media synthesis.

Zero-Cost Captions: Integrates OpenAI’s Whisper locally to generate precise, word-level timestamps without relying on expensive third-party APIs.

SSE State Management: Provides real-time feedback via Server-Sent Events (SSE), ensuring the user is constantly informed of the rendering status.

Decoupled Architecture: Separates the Python media engine from the React-based management dashboard for better scalability and maintenance.

---

## 📸 Interface Preview

### 1. Home (News-to-Script Transition)
![Home Dashboard](./assets/ui.jpg)
*Showing the data ingestion and Gemini transformation.*

### 2. Rendering Pulse
![Rendering Status](./assets/loading.jpg)
*Capturing the live progress bar and terminal activity.*

### 3. Mobile Preview
![Mobile Preview](./assets/vidui.jpg)
*The final vertical video served through the local static file server.*

---
🛠️ Installation & Setup
Backend (FastAPI)
Bash
# From root directory
python -m uvicorn server:app --reload --reload-dir .
Frontend (Next.js)
Bash
# From frontend directory
cd frontend
npm run dev
Alex Gurung | Graduate Student @ University of Michigan-Flint

Expected Graduation: April 30, 2026