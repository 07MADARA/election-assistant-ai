import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          firebase: ['firebase/app', 'firebase/auth', 'firebase/firestore'],
          utils: ['marked', 'dompurify', 'lucide-react']
        }
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
  },
})
