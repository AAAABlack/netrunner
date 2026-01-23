import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/static/',
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  },
  build: {
    outDir: '../static',
    // keep the outDir stable but let Vite emit hashed filenames so browsers pick up fresh builds
    emptyOutDir: false
  }
})