import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/predict': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/fighter-data': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/feature-importance': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/rag-query': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/rag-query-progress': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true,
      }
    }
  }
});
