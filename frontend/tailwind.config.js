/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#4A7C9D',
          light: '#F0F5F8',
        },
        surface: {
          bg: '#F5F5F5',
          card: '#FFFFFF',
        },
        border: {
          subtle: '#E5E7EB',
          medium: '#D1D5DB',
        },
        text: {
          primary: '#2C2C2C',
          secondary: '#6B7280',
        },
        status: {
          low: {
            text: '#166534',
            bg: '#DCFCE7',
          },
          moderate: {
            text: '#92400E',
            bg: '#FEF3C7',
          },
          high: {
            text: '#991B1B',
            bg: '#FEE2E2',
          }
        }
      },
      borderRadius: {
        'sm': '6px',
        'md': '8px',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
