module.exports = {
  content: ['./src.html'],
  theme: {
    extend: {
      colors: {
        alabaster: '#FAF8F5',
        sand: '#F2EFE9',
        charcoal: '#1E2229',
        sage: { DEFAULT: '#2E4A43', deep: '#223833', soft: '#E3E9E5' },
        gold: { DEFAULT: '#C5A059', deep: '#A9863F', soft: '#F3EBDA' },
        mist: '#6B7068'
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', 'Georgia', '"Times New Roman"', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif']
      },
      boxShadow: {
        soft: '0 20px 50px -24px rgba(30,34,41,.28)',
        lift: '0 30px 70px -30px rgba(46,74,67,.45)'
      }
    }
  }
};
