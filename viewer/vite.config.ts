import { defineConfig } from "vite";

const base = process.env.VITE_BASE_PATH || "/";

export default defineConfig({
  base: base.endsWith("/") ? base : `${base}/`,
  build: {
    target: "es2020",
    sourcemap: true,
  },
  test: {
    environment: "jsdom",
    include: ["src/tests/**/*.test.ts"],
    coverage: {
      reporter: ["text", "html"],
    },
  },
});
