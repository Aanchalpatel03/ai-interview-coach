"use client";

import { Github } from "lucide-react";

import { api } from "@/lib/api";

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5">
      <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.3-1.5 3.9-5.5 3.9-3.3 0-6-2.8-6-6.2s2.7-6.2 6-6.2c1.9 0 3.2.8 4 1.5l2.7-2.7C17.1 2.9 14.8 2 12 2 6.9 2 2.8 6.5 2.8 12s4.1 10 9.2 10c5.3 0 8.8-3.7 8.8-9 0-.6-.1-1.1-.1-1.5H12Z" />
      <path fill="#34A853" d="M3.9 7.3l3.2 2.4C8 7.2 9.8 5.8 12 5.8c1.9 0 3.2.8 4 1.5l2.7-2.7C17.1 2.9 14.8 2 12 2 8.5 2 5.4 4 3.9 7.3Z" />
      <path fill="#FBBC05" d="M12 22c2.7 0 5-1 6.7-2.6l-3.1-2.5c-.8.6-1.9 1.1-3.6 1.1-3.9 0-5.2-2.6-5.5-3.9l-3.1 2.4C5 20 8.2 22 12 22Z" />
      <path fill="#4285F4" d="M20.8 13c0-.6-.1-1.1-.1-1.5H12v3.9h5.5c-.3 1.4-1.3 2.7-2.9 3.6l3.1 2.5c1.8-1.7 3.1-4.2 3.1-8.5Z" />
    </svg>
  );
}

export function SocialLogin({ mode }: { mode: "login" | "signup" }) {
  return (
    <div className="mt-6 space-y-3">
      <div className="flex items-center gap-3 text-xs uppercase tracking-[0.3em] text-slate-500">
        <span className="h-px flex-1 bg-white/10" />
        <span>{mode === "login" ? "Or sign in with" : "Or create account with"}</span>
        <span className="h-px flex-1 bg-white/10" />
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <a
          href={api.getOAuthStartUrl("google")}
          className="flex items-center justify-center gap-3 rounded-2xl border border-white/12 bg-white/[0.04] px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.08]"
        >
          <GoogleIcon />
          <span>Google</span>
        </a>
        <a
          href={api.getOAuthStartUrl("github")}
          className="flex items-center justify-center gap-3 rounded-2xl border border-white/12 bg-white/[0.04] px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.08]"
        >
          <Github className="h-5 w-5" />
          <span>GitHub</span>
        </a>
      </div>
      <p className="text-xs text-slate-400">Google and GitHub sign-in work after OAuth client credentials are added in `backend/.env`.</p>
    </div>
  );
}
