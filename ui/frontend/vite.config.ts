import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const buildStartTime = new Date()
const buildTimeStr = buildStartTime.toLocaleString()
console.log(`🏗️  Starting frontend build at ${buildTimeStr}`)

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'build-time-logger',
      transformIndexHtml(html: string) {
        return html.replace('__BUILD_TIME__', buildTimeStr)
      },
      buildEnd: () => {
        const buildEndTime = new Date()
        const duration = (buildEndTime.getTime() - buildStartTime.getTime()) / 1000
        console.log(`✅ Frontend build completed at ${buildEndTime.toLocaleString()}`)
        console.log(`⏱️  Total build time: ${duration.toFixed(2)} seconds`)
        console.log(`📋 Build time will be displayed in browser console: ${buildTimeStr}`)
      }
    }
  ],
  base: '/ui/',
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
