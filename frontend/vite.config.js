import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 외부 접속 허용
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // FastAPI 서버 주소
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    },
    allowedHosts: ['icunix.iptime.org', 'localhost', '127.0.0.1'],
  }
})