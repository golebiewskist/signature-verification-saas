import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  // KLUCZOWE ZMIANY DLA DJANGO:
  base: '/static/', // Ścieżka bazowa dla plików statycznych w Django
  build: {
    outDir: '../backend/static/vue', // Budujemy bezpośrednio do folderu static w Django
    emptyOutDir: true,
    manifest: true, // Generuje manifest.json (przydatne przy cache'owaniu)
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name].js`,
        chunkFileNames: `assets/[name].js`,
        assetFileNames: `assets/[name].[ext]`
      }
    }
  }
})
