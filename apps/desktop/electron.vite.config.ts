import { resolve } from "node:path";
import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    resolve: {
      alias: {
        "@liketypeless/shared": resolve("../../packages/shared/src/index.ts")
      }
    }
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        output: {
          format: "cjs",
          entryFileNames: "[name].js"
        }
      }
    },
    resolve: {
      alias: {
        "@liketypeless/shared": resolve("../../packages/shared/src/index.ts")
      }
    }
  },
  renderer: {
    root: resolve("src/renderer"),
    server: {
      port: Number(process.env.LIKETYPELESS_RENDERER_PORT ?? "5173")
    },
    resolve: {
      alias: {
        "@liketypeless/shared": resolve("../../packages/shared/src/index.ts")
      }
    },
    plugins: [react()]
  }
});
