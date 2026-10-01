// ============================================================
//  Article loader — loads articles.json manifest and renders
//  the homepage list with cover thumbnails and hover previews
// ============================================================

async function loadArticleManifest() {
  try {
    const resp = await fetch('articles/articles.json')
    if (!resp.ok) return []
    return await resp.json()
  } catch (e) {
    console.error('No articles.json found.')
    return []
  }
}

async function renderArticleList() {
  const container = document.getElementById('article-list')
  if (!container) return

  const articles = await loadArticleManifest()

  if (articles.length === 0) {
    container.innerHTML = '<p class="subtitle">No articles published yet. Check back soon.</p>'
    return
  }

  container.innerHTML = articles.map(article => {
    const preview = (article.preview || article.summary || '').substring(0, 200)
    const previewSuffix = preview.length >= 200 ? '...' : ''
    const coverSrc = `images/cover-${article.id}.jpg`
    const author = article.author || ''

    return `
      <a class="article-card" href="article.html?id=${article.id}">
        <div class="card-cover">
          <img src="${coverSrc}" alt="${article.title}" loading="lazy">
        </div>
        <div class="card-content">
          <h2>${article.title}</h2>
          <div class="card-date">${article.date || ''}</div>
          ${author ? `<div class="card-author">${author}</div>` : ''}
          <div class="card-preview">${preview}${previewSuffix}</div>
        </div>
      </a>
    `
  }).join('')
}

// Auto-run on homepage
if (document.getElementById('article-list')) {
  renderArticleList()
}