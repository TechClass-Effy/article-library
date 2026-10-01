// ============================================================
//  Theme toggle — saves user preference in localStorage
// ============================================================

function toggleTheme() {
  const current = document.getElementById('theme-stylesheet').href.includes('dark') ? 'dark' : 'light'
  const newTheme = current === 'dark' ? 'light' : 'dark'
  applyTheme(newTheme)
  localStorage.setItem('article-library-theme', newTheme)
}

function applyTheme(theme) {
  const link = document.getElementById('theme-stylesheet')
  link.href = `assets/theme-${theme}.css`
  const icon = document.getElementById('theme-icon')
  if (icon) {
    icon.textContent = theme === 'dark' ? '☀️' : '🌙'
  }
}

// Load saved theme on page load
(function() {
  const saved = localStorage.getItem('article-library-theme') || 'dark'
  applyTheme(saved)
})()