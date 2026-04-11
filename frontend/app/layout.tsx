import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppProvider } from "@/components/providers/app-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Interview Coach",
  description: "Practice interviews with AI-powered question generation, live posture analysis, and personalized feedback.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}
