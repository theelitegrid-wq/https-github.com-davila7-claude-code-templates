module.exports = {
  content: ['./src.html'],
  theme: {
    extend: {
      colors: {
        mist: '#F8FAFC',
        navy: { DEFAULT: '#0F172A', 2: '#1E293B' },
        cyan: { DEFAULT: '#0EA5E9', deep: '#0284C7', soft: '#E0F2FE' },
        gold: { DEFAULT: '#D97706', soft: '#FEF3C7', light: '#FBBF24' }
      },
      fontFamily: {
        display: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif'],
        sans: ['Inter', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif']
      },
      boxShadow: {
        soft: '0 18px 50px -24px rgba(15,23,42,.28)',
        lift: '0 30px 70px -30px rgba(14,165,233,.45)'
      }
    }
  }
};
