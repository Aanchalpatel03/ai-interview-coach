"use client";

import { ChangeEvent, useState } from "react";

export function ResumePanel({
  resumeUrl,
  skills,
  roles,
  onUpload,
}: {
  resumeUrl?: string | null;
  skills: string[];
  roles: string[];
  onUpload: (file: File) => Promise<void>;
}) {
  const [uploading, setUploading] = useState(false);

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await onUpload(file);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div id="resume" className="panel p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold">Resume intelligence</h2>
          <p className="text-sm text-slate-400">Upload a resume to tailor question generation and role recommendations.</p>
        </div>
        <label className="rounded-full bg-gradient-to-r from-signal to-coral px-5 py-3 text-sm font-semibold text-white shadow-glow">
          {uploading ? "Uploading..." : "Upload resume"}
          <input type="file" accept=".pdf,.docx" className="hidden" onChange={handleFile} />
        </label>
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-[1.5rem] bg-white/[0.04] p-4">
          <p className="text-sm font-semibold text-slate-100">Detected skills</p>
          <p className="mt-2 text-sm text-slate-300">{skills.length ? skills.join(", ") : "No resume analyzed yet."}</p>
        </div>
        <div className="rounded-[1.5rem] bg-white/[0.04] p-4">
          <p className="text-sm font-semibold text-slate-100">Suggested roles</p>
          <p className="mt-2 text-sm text-slate-300">{roles.length ? roles.join(", ") : "Upload a resume to unlock recommendations."}</p>
        </div>
      </div>
      {resumeUrl && <p className="mt-4 text-sm text-slate-400">Stored resume: {resumeUrl}</p>}
    </div>
  );
}
