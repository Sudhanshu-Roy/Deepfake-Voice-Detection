import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const fileEnv = loadEnv(mode, process.cwd(), "VITE_");
  const apiBase = (
    process.env.VITE_API_BASE_URL ||
    fileEnv.VITE_API_BASE_URL ||
    ""
  ).trim();

  if (mode === "production" && !apiBase) {
    throw new Error(
      "Set VITE_API_BASE_URL before building the frontend."
    );
  }

  return {};
});
