"use client";

import { useEffect, useRef } from "react";

import { LiveFeedback } from "@/types";

const tone = {
  green: "border-emerald-400/50 bg-emerald-400/15 text-emerald-100",
  yellow: "border-amber-400/50 bg-amber-400/15 text-amber-100",
  red: "border-rose-400/50 bg-rose-400/15 text-rose-100",
};

export function VideoFeed({ onFrame, feedback }: { onFrame: (frame: string) => void; feedback: LiveFeedback | null }) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const onFrameRef = useRef(onFrame);

  useEffect(() => {
    onFrameRef.current = onFrame;
  }, [onFrame]);

  useEffect(() => {
    let interval: number | undefined;
    let stream: MediaStream | undefined;

    async function boot() {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      interval = window.setInterval(() => {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        if (!video || !canvas) return;
        const context = canvas.getContext("2d");
        if (!context) return;
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 360;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        onFrameRef.current(canvas.toDataURL("image/jpeg", 0.6));
      }, 4000);
    }

    void boot();

    return () => {
      if (interval) window.clearInterval(interval);
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return (
    <div className="panel overflow-hidden p-3">
      <div className="mb-3 flex items-center justify-between rounded-[1.5rem] border border-white/10 bg-night/80 px-4 py-3 text-white">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-white/60">Camera feed</p>
          <p className="text-sm font-medium">Realtime posture and expression capture</p>
        </div>
        <span className="h-3 w-3 rounded-full bg-emerald-400" />
      </div>
      <div className="relative">
        <video ref={videoRef} autoPlay muted playsInline className="aspect-video w-full rounded-3xl bg-slate-900 object-cover" />
        {feedback ? (
          <div className="pointer-events-none absolute inset-0 flex flex-col justify-between p-4">
            <div className="flex flex-wrap gap-2">
              <div className={`rounded-full border px-3 py-2 text-xs font-semibold backdrop-blur ${tone[feedback.status as keyof typeof tone] ?? tone.yellow}`}>
                Confidence {feedback.confidence}
              </div>
              <div className="rounded-full border border-white/15 bg-night/55 px-3 py-2 text-xs text-white backdrop-blur">
                Eye contact {feedback.eye_contact}
              </div>
              <div className="rounded-full border border-white/15 bg-night/55 px-3 py-2 text-xs text-white backdrop-blur">
                Posture {feedback.posture}
              </div>
            </div>
            <div className="ml-auto max-w-sm rounded-[1.5rem] border border-white/15 bg-night/70 p-3 text-sm text-white backdrop-blur">
              <p className="text-xs uppercase tracking-[0.2em] text-white/60">Live overlay</p>
              <div className="mt-2 space-y-1">
                {feedback.suggestions.map((suggestion) => <p key={suggestion}>{suggestion}</p>)}
              </div>
            </div>
          </div>
        ) : null}
      </div>
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
