import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy /api/* to the FastAPI backend so the browser only talks to one
// origin (Vite). Avoids CORS during dev and keeps the frontend code
// agnostic of where the backend actually lives in production.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
});
