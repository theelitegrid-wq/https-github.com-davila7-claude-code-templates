module.exports = {
  content: ['./src.html'],
  theme: {
    extend: {
      colors: {
        porcelain: '#F8FAFC',
        ice: '#EFF6FF',
        navy: { DEFAULT: '#0F172A', 2: '#1E293B' },
        pacific: { DEFAULT: '#0284C7', deep: '#0369A1', soft: '#E0F2FE' },
        amber: { DEFAULT: '#D97706', soft: '#FEF3C7' }
      },
      fontFamily: {
        display: ['Outfit', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif'],
        sans: ['Inter', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif']
      },
      boxShadow: {
        soft: '0 18px 50px -24px rgba(15,23,42,.30)',
        lift: '0 30px 70px -30px rgba(2,132,199,.45)'
      }
    }
  }
};
