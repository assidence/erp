import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            // Only strip trailing slash from DELETE requests with numeric IDs
            // (e.g. DELETE /api/customers/2/ → DELETE /api/customers/2)
            // Other methods (GET, POST, PUT) must keep trailing slash
            if (req.method === 'DELETE' && req.url && req.url.endsWith('/') && req.url !== '/') {
              req.url = req.url.replace(/\/$/, '')
              proxyReq.path = req.url
            }
          })
        }
      },
      '/upload': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
