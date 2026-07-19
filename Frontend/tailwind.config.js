/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep obsidian canvas base, as specified by the user's design preference
        slate: {
          950: '#090d16', 
          900: '#0f172a',
        }
      }
    },
  },
  plugins: [],
}
