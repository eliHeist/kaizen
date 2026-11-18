import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

// Builds src/main.ts into public/dist/bundle.{js,css}, the paths that
// templates/base.html loads via {% static 'dist/...' %}. Django serves
// static/public/ through STATICFILES_DIRS, so there is no Vite dev server
// in the loop: use `pnpm dev` (build --watch) while editing.
export default defineConfig({
    plugins: [
        tailwindcss(),
    ],
    // public/ is Django's static dir (and contains outDir), not a Vite public dir.
    publicDir: false,
    // Fonts and images referenced from CSS resolve relative to bundle.css.
    base: './',
    build: {
        outDir: 'public/dist',
        emptyOutDir: true,
        sourcemap: true,
        rollupOptions: {
            input: { bundle: 'src/main.ts' },
            output: {
                entryFileNames: '[name].js',
                chunkFileNames: '[name].js',
                assetFileNames: (asset) =>
                    asset.names?.some((n) => n.endsWith('.css'))
                        ? '[name][extname]'
                        : 'assets/[name]-[hash][extname]',
            },
        },
    },
})
