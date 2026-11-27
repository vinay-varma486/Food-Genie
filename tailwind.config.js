/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./*.{js,ts,jsx,tsx}",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        lavender: {
          mist: '#F2ECFF',
          light: '#FAF7FF',
          DEFAULT: '#F2ECFF',
          dark: '#E5DAFB',
          border: '#D8C5FF',
        },
        royal: {
          DEFAULT: '#351078',
          deep: '#230852',
          light: '#4C18AB',
          surface: '#2C0D64',
          accent: '#5E22CE',
        },
        lime: {
          electric: '#C6FF00',
          DEFAULT: '#C6FF00',
          hover: '#B5EA00',
          muted: '#A5D600',
          dark: '#2F5200',
        },
        lightblue: {
          DEFAULT: '#ADD8E6',
          soft: '#EEF8FC',
          deep: '#1E5F74',
        },
        brand: {
          DEFAULT: '#351078',
          dark: '#230852',
          light: '#F2ECFF',
          border: '#ADD8E6',
          muted: '#ADD8E6',
        },
        surface: {
          bg: '#F2ECFF',
          card: '#FFFFFF',
          border: '#E5DAFB',
        },
        ink: {
          primary: '#230852',
          secondary: '#5B4B7A',
        },
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 8px 24px -6px rgba(53, 16, 120, 0.08), 0 2px 6px -2px rgba(53, 16, 120, 0.04)',
        'glow-purple': '0 10px 25px -8px rgba(53, 16, 120, 0.25)',
      },
    },
  },
  plugins: [],
};
