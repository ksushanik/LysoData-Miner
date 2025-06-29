import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    chunkSizeWarningLimit: 1000,
  },
  preview: {
    port: 3000,
  },
  resolve: {
    alias: {
      'components': path.resolve(__dirname, 'src/components'),
      'pages': path.resolve(__dirname, 'src/pages'),
      'services': path.resolve(__dirname, 'src/services'),
      'types': path.resolve(__dirname, 'src/types'),
      'hooks': path.resolve(__dirname, 'src/hooks'),
    }
  }
}) 