/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom Brand Palette
        'brand-primary': {
          light: '#60a5fa', // blue-400
          DEFAULT: '#3b82f6', // blue-500
          dark: '#2563eb', // blue-600
        },
        'brand-neutral': {
          lightest: '#f8fafc', // slate-50
          light: '#f1f5f9',    // slate-100
          DEFAULT: '#e2e8f0',   // slate-200
          dark: '#64748b',     // slate-500
          darkest: '#1e293b',  // slate-800
        },
        'brand-success': '#22c55e', // green-500
        'brand-danger': '#ef4444',  // red-500

        // Standard Semantic Palette (for compatibility)
        border: 'var(--brand-neutral, #e2e8f0)',
        background: 'var(--brand-neutral-lightest, #f8fafc)',
        foreground: 'var(--brand-neutral-darkest, #1e293b)',
        primary: {
          DEFAULT: 'var(--brand-primary, #3b82f6)',
          foreground: 'var(--brand-neutral-lightest, #f8fafc)',
        },
        muted: {
          DEFAULT: 'var(--brand-neutral-light, #f1f5f9)',
          foreground: 'var(--brand-neutral-dark, #64748b)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 