/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/*.html', './**/templates/**/*.html'],
  theme: {
    extend: {
      colors: {
        primary: {
          900: 'rgb(16, 43, 16)',
          800: 'rgb(13, 40, 13)',
          100: 'rgb(237, 250, 237)',
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
