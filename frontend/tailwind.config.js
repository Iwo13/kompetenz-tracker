/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'fhnw-navy':   '#003366',
        'fhnw-yellow': '#FDE70E',
        'fhnw-light':  '#D5E8F0',
      },
    },
  },
  plugins: [],
};
