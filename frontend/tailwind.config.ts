import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#f8fafc",
        frost: "#050816",
        signal: "#3b82f6",
        ember: "#f59e0b",
        moss: "#10b981",
        coral: "#22d3ee",
        dune: "#111827",
        night: "#030712",
      },
      fontFamily: {
        sans: ["'Space Grotesk'", "ui-sans-serif", "system-ui"],
      },
      boxShadow: {
        panel: "0 24px 80px rgba(2, 8, 23, 0.45)",
        glow: "0 18px 50px rgba(59, 130, 246, 0.28)",
      },
    },
  },
  plugins: [],
};

export default config;
