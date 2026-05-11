import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  // WHY: Tailwind v4 integrates via a Vite plugin (no `tailwind.config.*` needed for basic setups).
  plugins: [react(), tailwindcss()],
})
