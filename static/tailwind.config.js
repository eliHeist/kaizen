module.exports = {
    content: ['../templates/*.html', '../**/templates/**/*.html'],
    darkMode: 'media', // or 'class'
    theme: {
        extend: {
            colors: {
                primary: {
                    950: 'rgb(63, 63, 19)',
                    900: '#797931',
                    800: '#d8d185',
                    100: '#f0ea86',
                },
                lead: '#ccc',
                grey: {
                    50: 'rgb(252, 252, 252)',
                    100: 'rgb(245, 245, 245)',
                    200: 'rgb(234, 234, 234)',
                    300: 'rgb(219, 219, 219)',
                    400: 'rgb(175, 175, 175)',
                    500: 'rgb(130, 130, 130)',
                    600: 'rgb(97, 97, 97)',
                    700: 'rgb(69, 69, 69)',
                    800: 'rgb(42, 42, 42)',
                    900: 'rgb(28, 28, 28)'
                }
            },
            fontFamily: {
                body: ['Poppins', 'sans-serif'],
                lead: ['Courgette', 'cursive'],
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
    variants: {
        extend: {},
    },
    plugins: [],
};
