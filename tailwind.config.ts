import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // Bloomberg terminal palette
        terminal: {
          bg: "#080c14",
          surface: "#0d1117",
          panel: "#111827",
          border: "#1e2d3d",
          muted: "#1a2332",
        },
        brand: {
          primary: "#0077ff",
          secondary: "#00a8ff",
          dim: "#003d80",
        },
        status: {
          success: "#00d084",
          warning: "#f5a623",
          error: "#ff3b47",
          info: "#0077ff",
        },
        data: {
          green: "#00d084",
          red: "#ff3b47",
          blue: "#0077ff",
          amber: "#f5a623",
          teal: "#00c4b8",
          purple: "#7c3aed",
        },
      },
      fontFamily: {
        mono: ["'IBM Plex Mono'", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
