import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite配置文件
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // API代理，将/api请求转发到后端
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
