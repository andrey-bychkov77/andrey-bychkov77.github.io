module.exports = {
  content: [
    './layouts/**/*.html',
    './content/**/*.{html,md}',
  ],
  theme: {
    extend: {
      colors: {
        'menu-active': '#5091B1',
        'menu-inactive': '#A1BBD1',
      },
      fontFamily: {
        'sans': ['PT Sans', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
