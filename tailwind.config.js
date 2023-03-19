/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/*.html', './**/templates/**/*.html'],
  theme: {
    extend: {
      colors: {
        primary: {
          900: '#797931',
          800: '#d8d185',
          100: '#f0ea86',
        },
        lead: '#ccc',
        grey: {
          900: 'hsl(0, 0%, 10%)',
          800: 'hsl(0, 0%, 20%)',
          700: 'hsl(0, 0%, 30%)',
          600: 'hsl(0, 0%, 40%)',
          500: 'hsl(0, 0%, 50%)',
          400: 'hsl(0, 0%, 60%)',
          300: 'hsl(0, 0%, 70%)',
          200: 'hsl(0, 0%, 80%)',
          100: 'hsl(0, 0%, 90%)',
          50: 'hsl(0, 0%, 98%)',
        }
      },
      fontFamily: {
        body: ['poppins']
      },
      aspectRatio: {
        surface: "4 / 3",
        1610: "16 / 10"
      },
      grayscale: {
        10: '10%',
      },
      flex: {
        base: '1',
        2: '2 2 0%',
        3: '6 6 0%',
      }
    },
  },
  plugins: [],
}
