/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        foreground: '#f8fafc',
        card: '#111827',
        border: '#1f2937',
        primary: {
          DEFAULT: '#3b82f6',
          foreground: '#ffffff',
        },
        accent: {
          DEFAULT: '#10b981',
          foreground: '#ffffff',
        }
      },
    },
  },
  plugins: [],

};
