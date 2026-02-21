"use client";
import { useState, useEffect } from "react";

export default function ReviewDashboard() {
  const [title, setTitle] = useState("");
  const [script, setScript] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [videoUrl, setVideoUrl] = useState("");

  const fetchDraft = async () => {
    setLoading(true);
    setVideoUrl(""); // Reset video if fetching new news
    setProgress(0);
    try {
      const res = await fetch("http://localhost:8000/api/news-draft");
      const data = await res.json();
      setTitle(data.title);
      setScript(data.script);
    } catch (err) {
      setStatus("Error fetching draft. Is the backend running?");
    }
    setLoading(false);
  };

  const startRender = async () => {
    setStatus("Rendering...");
    setVideoUrl("");
    setProgress(0);

    // 1. Start listening to the Progress Stream (SSE)
    const eventSource = new EventSource("http://localhost:8000/api/progress");
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.percent);
      
      if (data.percent >= 100) {
        setStatus("Render Complete! 🎉");
        eventSource.close();
        // Point to the static file endpoint on your Python server
        setVideoUrl(`http://localhost:8000/static/final_video.mp4?t=${Date.now()}`);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    // 2. Trigger the actual render
    try {
      await fetch("http://localhost:8000/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, script }),
      });
    } catch (err) {
      setStatus("Error starting render.");
      eventSource.close();
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-white p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="border-b border-zinc-800 pb-4 flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">AI Video Factory</h1>
            <p className="text-zinc-400">Tech News Daily Videos</p>
          </div>
          <div className="text-right text-xs text-zinc-600 font-mono">
            V1.0.0 Stable
          </div>
        </header>

        <button 
          onClick={fetchDraft}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-semibold transition-all disabled:opacity-50"
        >
          {loading ? "Generating Draft..." : "Get Today's News"}
        </button>

        {title && (
          <div className="space-y-4 animate-in fade-in duration-500">
            <input 
              type="text" 
              value={title} 
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-xl font-semibold outline-none"
            />
            <textarea 
              value={script} 
              onChange={(e) => setScript(e.target.value)}
              rows={6}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-4 font-mono text-zinc-300 outline-none"
            />
            
            {!videoUrl && status !== "Rendering..." && (
              <button 
                onClick={startRender}
                className="w-full bg-green-600 hover:bg-green-700 py-4 rounded-xl text-lg font-bold transition-all"
              >
                Confirm & Render Video 🚀
              </button>
            )}
          </div>
        )}

        {/* PROGRESS BAR SECTION */}
        {status === "Rendering..." && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm font-mono text-zinc-400">
              <span>System Processing...</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-zinc-900 h-3 rounded-full overflow-hidden border border-zinc-800">
              <div 
                className="bg-blue-500 h-full transition-all duration-700 ease-in-out" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* VIDEO PLAYER SECTION */}
        {videoUrl && (
          <div className="mt-8 space-y-4 animate-in zoom-in duration-300">
            <h2 className="text-xl font-bold text-green-400 flex items-center gap-2">
              <span>Ready for Review</span>
            </h2>
            <div className="aspect-[9/16] max-w-[350px] mx-auto border-4 border-zinc-800 rounded-2xl overflow-hidden shadow-2xl bg-black">
              <video controls autoPlay className="w-full h-full">
                <source src={videoUrl} type="video/mp4" />
              </video>
            </div>
          </div>
        )}

        {status && !videoUrl && status !== "Rendering..." && (
          <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-lg text-center text-zinc-400">
            {status}
          </div>
        )}
      </div>
    </main>
  );
}