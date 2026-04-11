"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { SocialLogin } from "@/components/auth/social-login";
import { useAppContext } from "@/components/providers/app-provider";
import { api } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const { setToken } = useAppContext();
  const [form, setForm] = useState({ name: "", email: "", password: "" });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const result = await api.signup(form);
    setToken(result.access_token);
    router.push("/dashboard");
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <form onSubmit={handleSubmit} className="panel w-full border border-white/8 p-8">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Start training</p>
        <h1 className="mt-3 text-4xl font-bold">Create account</h1>
        <div className="mt-6 space-y-4">
          <input className="w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4" type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <button className="w-full rounded-full bg-gradient-to-r from-signal to-coral px-6 py-4 font-semibold text-white shadow-glow">Create account</button>
        </div>
        <SocialLogin mode="signup" />
      </form>
    </main>
  );
}
