/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1e40af',
          light: '#3b82f6',
          dark: '#1e3a8a'
        },
        success: {
          DEFAULT: '#059669',
          light: '#10b981',
          dark: '#047857'
        },
        danger: {
          DEFAULT: '#dc2626',
          light: '#ef4444',
          dark: '#b91c1c'
        },
        warning: {
          DEFAULT: '#d97706',
          light: '#f59e0b',
          dark: '#b45309'
        },
        tech: {
          cyan: '#06b6d4',
          blue: '#2563eb',
          violet: '#7c3aed'
        }
      },
      fontFamily: {
        sans: ['Inter', 'PingFang SC', 'Microsoft YaHei', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        soft: '0 18px 45px rgba(15, 23, 42, 0.08)',
        glow: '0 12px 34px rgba(37, 99, 235, 0.18), 0 0 24px rgba(6, 182, 212, 0.16)',
        'glow-lg': '0 18px 44px rgba(37, 99, 235, 0.24), 0 0 34px rgba(6, 182, 212, 0.22)'
      },
      keyframes: {
        breath: {
          '0%, 100%': { opacity: '0.55', transform: 'scale(1)' },
          '50%': { opacity: '0.9', transform: 'scale(1.08)' }
        },
        'breath-slow': {
          '0%, 100%': { opacity: '0.45', transform: 'scale(1)' },
          '50%': { opacity: '0.75', transform: 'scale(1.12)' }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' }
        }
      },
      animation: {
        breath: 'breath 5.5s ease-in-out infinite',
        'breath-slow': 'breath-slow 8s ease-in-out infinite',
        float: 'float 4.5s ease-in-out infinite'
      }
    }
  },
  plugins: []
}
