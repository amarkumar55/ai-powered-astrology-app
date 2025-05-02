/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.{html,js}',   // Django templates location
    './static/js/**/*.{js,jsx}',    // Your JS files
  ],
  theme: {
    extend: {},
  },
    plugins: [
        function({ addVariant }) {
        addVariant('peer-checked', '&:checked ~ .peer-checked\\:block');
      }
  ],
}