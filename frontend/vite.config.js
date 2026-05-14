import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'fix-charset',
      transformIndexHtml(html) {
        // Ensure charset meta is the FIRST thing in <head>
        return html.replace(
          '<head>',
          '<head><meta charset="UTF-8" />'
        )
      },
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          const origEnd = res.end
          res.end = function (...args) {
            if (!res.headersSent) {
              const ct = res.getHeader('Content-Type')
              if (typeof ct === 'string' && ct.startsWith('text/') && !ct.includes('charset')) {
                res.setHeader('Content-Type', ct + '; charset=utf-8')
              }
            }
            return origEnd.call(this, ...args)
          }
          next()
        })
      }
    }
  ],
  server: {
    host: '0.0.0.0',
    port: 3002,
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
