"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { SocialLogin } from "@/components/auth/social-login";
import { useAppContext } from "@/components/providers/app-provider";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { setToken } = useAppContext();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setError(params.get("error"));
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const result = await api.login({ email, password });
    setToken(result.access_token);
    router.push("/dashboard");
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <form onSubmit={handleSubmit} className="panel w-full border border-white/8 p-8">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Welcome back</p>
        <h1 className="mt-3 text-4xl font-bold">Login</h1>
        {error ? <p className="mt-4 rounded-2xl border border-amber-400/30 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">{error}</p> : null}
        <div className="mt-6 space-y-4">
          <input className="w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input className="w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button className="w-full rounded-full bg-gradient-to-r from-signal to-coral px-6 py-4 font-semibold text-white shadow-glow">Continue</button>
        </div>
        <SocialLogin mode="login" />
      </form>
    </main>
  );
}
