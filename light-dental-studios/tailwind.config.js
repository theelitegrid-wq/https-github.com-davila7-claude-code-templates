module.exports = {
  content: ['./src.html'],
  theme: {
    extend: {
      colors: {
        sky: { light: '#F0F9FF', 100: '#E0F2FE', 200: '#BAE6FD', 300: '#7DD3FC' },
        slate: { ink: '#0F172A' },
        ink: '#0F172A',
        cerulean: { DEFAULT: '#0284C7', deep: '#0369A1', soft: '#E0F2FE' },
        sun: { DEFAULT: '#F59E0B', deep: '#B45309', soft: '#FEF3C7' }
      },
      fontFamily: {
        display: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif'],
        sans: ['Inter', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif']
      },
      boxShadow: {
        soft: '0 18px 50px -24px rgba(15,23,42,.28)',
        lift: '0 30px 70px -30px rgba(2,132,199,.45)',
        glow: '0 20px 50px -20px rgba(245,158,11,.55)'
      }
    }
  }
};
