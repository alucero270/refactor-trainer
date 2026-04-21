import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            "/candidates": "http://127.0.0.1:8000",
            "/exercise": "http://127.0.0.1:8000",
            "/github": "http://127.0.0.1:8000",
            "/health": "http://127.0.0.1:8000",
            "/hints": "http://127.0.0.1:8000",
            "/provider": "http://127.0.0.1:8000",
            "/providers": "http://127.0.0.1:8000",
            "/submit-attempt": "http://127.0.0.1:8000",
            "/submit-code": "http://127.0.0.1:8000",
        },
    },
});
