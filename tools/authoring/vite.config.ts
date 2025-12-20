import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: '.',
  server: {
    port: 5173,
    fs: {
      // Allow serving files from the parent directories (to access schemas)
      allow: ['..', '../..']
    }
  },
  resolve: {
    alias: {
      '@schemas': path.resolve(__dirname, '../../schemas')
    }
  }
});
