import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Use relative asset paths so the app can be hosted under any path
  base: './',
  server: {
    port: 5173
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
});
