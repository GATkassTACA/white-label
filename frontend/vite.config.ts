import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Build configuration
  build: {
    outDir: '../app/static/dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
        chat: path.resolve(__dirname, 'src/pages/chat.html'),
        documents: path.resolve(__dirname, 'src/pages/documents.html'),
        wizard: path.resolve(__dirname, 'src/pages/wizard.html')
      },
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  
  // Development server
  server: {
    port: 3000,
    host: true,
    proxy: {
      // Proxy API calls to Flask backend
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true
      }
    }
  },
  
  // Path resolution
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@styles': path.resolve(__dirname, './src/styles'),
      '@assets': path.resolve(__dirname, './src/assets')
    }
  },
  
  // CSS configuration
  css: {
    postcss: './postcss.config.js',
    modules: {
      localsConvention: 'camelCaseOnly'
    }
  },
  
  // Environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString())
  }
})
