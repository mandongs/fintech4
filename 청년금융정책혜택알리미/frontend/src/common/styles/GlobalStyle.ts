import { createGlobalStyle } from 'styled-components'

export const theme = {
  colors: {
    primary: '#4F46E5',       // indigo-600
    primaryLight: '#818CF8',  // indigo-400
    primaryDark: '#3730A3',   // indigo-800
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    bg: '#F8FAFC',
    surface: '#FFFFFF',
    border: '#E2E8F0',
    textPrimary: '#0F172A',
    textSecondary: '#64748B',
    textMuted: '#94A3B8',
  },
  radius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
  },
  shadow: {
    sm: '0 1px 3px rgba(0,0,0,0.06)',
    md: '0 4px 12px rgba(0,0,0,0.08)',
    lg: '0 8px 24px rgba(0,0,0,0.10)',
  },
}

export const GlobalStyle = createGlobalStyle`
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { font-size: 16px; }
  body {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: ${theme.colors.bg};
    color: ${theme.colors.textPrimary};
    -webkit-font-smoothing: antialiased;
  }
  a { color: inherit; text-decoration: none; }
  button { cursor: pointer; border: none; background: none; font: inherit; }
  input, textarea, select { font: inherit; }
`
