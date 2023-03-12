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
        lead: '#ccc'
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
