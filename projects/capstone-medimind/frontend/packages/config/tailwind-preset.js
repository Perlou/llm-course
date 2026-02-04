/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        // 主色调
        background: '#f8fafc',
        card: '#ffffff',
        border: '#e2e8f0',
        
        // 强调色
        medical: {
          blue: '#0ea5e9',
          green: '#22c55e',
          purple: '#8b5cf6',
        },
        
        // 警示色
        alert: {
          warning: '#f97316',
          danger: '#ef4444',
          notice: '#eab308',
        },
        
        // 文字色
        text: {
          primary: '#1e293b',
          secondary: '#64748b',
          muted: '#94a3b8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'PingFang SC', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        xs: '12px',
        sm: '14px',
        base: '16px',
        lg: '18px',
        xl: '20px',
        '2xl': '24px',
      },
      spacing: {
        1: '4px',
        2: '8px',
        3: '12px',
        4: '16px',
        6: '24px',
        8: '32px',
      },
      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        full: '9999px',
      },
      animation: {
        'message-in': 'messageIn 0.3s ease-out',
        typing: 'typing 1.4s infinite ease-in-out',
      },
      keyframes: {
        messageIn: {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        typing: {
          '0%, 80%, 100%': { transform: 'scale(0.8)', opacity: '0.5' },
          '40%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
