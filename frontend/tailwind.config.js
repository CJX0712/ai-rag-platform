/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Token-driven palette. Components only ever use these names;
        // the actual values live as CSS variables in src/index.css.
        bg: "var(--c-bg)",
        surface: "var(--c-surface)",
        border: "var(--c-border)",
        text: "var(--c-text)",
        muted: "var(--c-muted)",
        primary: "var(--c-primary)",
        "primary-fg": "var(--c-primary-fg)",
        accent: "var(--c-accent)",
      },
    },
  },
  plugins: [],
};
