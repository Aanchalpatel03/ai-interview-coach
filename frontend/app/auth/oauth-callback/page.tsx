"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAppContext } from "@/components/providers/app-provider";

export default function OAuthCallbackPage() {
  const router = useRouter();
  const { setToken } = useAppContext();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    const error = params.get("error");

    if (token) {
      setToken(token);
      router.replace("/dashboard");
      return;
    }

    router.replace(error ? `/auth/login?error=${encodeURIComponent(error)}` : "/auth/login");
  }, [router, setToken]);

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <div className="panel w-full border border-white/8 p-8 text-center">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Authentication</p>
        <h1 className="mt-3 text-3xl font-bold text-white">Signing you in...</h1>
        <p className="mt-3 text-sm text-slate-300">You will be redirected as soon as the provider finishes authentication.</p>
      </div>
    </main>
  );
}
