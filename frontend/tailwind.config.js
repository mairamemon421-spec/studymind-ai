/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Deep space dark palette
        dark: {
          950: '#05050f',
          900: '#0a0a1a',
          800: '#0f0f25',
          700: '#151530',
          600: '#1c1c3d',
          500: '#242450',
        },
        // Purple accent
        purple: {
          50:  '#f5f0ff',
          100: '#ede0ff',
          200: '#dbc4ff',
          300: '#c49eff',
          400: '#a970ff',
          500: '#9047ff',
          600: '#7b2fff',
          700: '#671ef7',
          800: '#561ed1',
          900: '#471caa',
          950: '#2c0f72',
        },
        // Teal accent
        teal: {
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
        },
        // Amber for warnings/exams
        amber: {
          400: '#fbbf24',
          500: '#f59e0b',
        },
        // Glass surfaces
        glass: {
          white: 'rgba(255,255,255,0.04)',
          border: 'rgba(255,255,255,0.08)',
          hover:  'rgba(255,255,255,0.07)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-mesh': 'radial-gradient(at 40% 20%, hsla(263,90%,30%,0.3) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(189,80%,25%,0.2) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(263,70%,20%,0.15) 0px, transparent 50%)',
        'glow-purple': 'radial-gradient(circle at center, rgba(144,71,255,0.15) 0%, transparent 70%)',
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glass': '0 4px 24px -1px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)',
        'glass-lg': '0 8px 40px -4px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08)',
        'purple-glow': '0 0 30px rgba(144,71,255,0.3)',
        'teal-glow': '0 0 20px rgba(20,184,166,0.2)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'typing': 'typing 1.5s steps(3) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-16px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        typing: {
          '0%': { content: '.' },
          '33%': { content: '..' },
          '66%': { content: '...' },
          '100%': { content: '' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(144,71,255,0.3)' },
          '100%': { boxShadow: '0 0 40px rgba(144,71,255,0.6)' },
        },
      },
    },
  },
  plugins: [],
}
