// ============================================================
//  Article reader — loads individual article, renders it,
//  and handles PDF download via browser print dialog
// ============================================================

async function loadArticleManifest() {
  try {
    const resp = await fetch('articles/articles.json')
    if (!resp.ok) return []
    return await resp.json()
  } catch (e) { return [] }
}

async function loadArticleContent(articleId) {
  try {
    const resp = await fetch(`articles/${articleId}.html`)
    if (!resp.ok) return null
    return await resp.text()
  } catch (e) { return null }
}

async function loadCurrentArticle() {
  const params = new URLSearchParams(window.location.search)
  const articleId = params.get('id')

  if (!articleId) {
    document.getElementById('article-title').textContent = 'Article Not Found'
    document.getElementById('article-body').innerHTML = '<p>No article ID specified.</p>'
    return
  }

  const articles = await loadArticleManifest()
  const meta = articles.find(a => a.id === articleId)

  if (!meta) {
    document.getElementById('article-title').textContent = 'Article Not Found'
    document.getElementById('article-body').innerHTML = `<p>Article "${articleId}" does not exist.</p>`
    return
  }

  document.title = `${meta.title} — Article Library`
  document.getElementById('article-title').textContent = meta.title
  document.getElementById('article-date').textContent = meta.date || ''

  const content = await loadArticleContent(articleId)
  if (content) {
    document.getElementById('article-body').innerHTML = content
  } else {
    document.getElementById('article-body').innerHTML = '<p>This article has no content yet.</p>'
  }

  // Trigger fade-in transition
  const container = document.getElementById('article-container')
  if (container) {
    requestAnimationFrame(() => {
      container.classList.add('loaded')
    })
  }

  window.currentArticle = meta

  // Show related articles at the bottom
  renderRelatedArticles(articles, articleId)
}

// ============================================================
//  Related Articles — shows "Read Next" suggestions at the
//  bottom of each article, linking to other articles.
// ============================================================

function renderRelatedArticles(allArticles, currentArticleId) {
  const container = document.getElementById('related-articles')
  if (!container) return

  // Get all articles except the current one
  const related = allArticles.filter(a => a.id !== currentArticleId)

  if (related.length === 0) {
    container.style.display = 'none'
    return
  }

  container.innerHTML = '<h2 class="section-heading-orange">Other Articles</h2>' +
    '<div class="related-list">' +
    related.map(article => {
      const coverSrc = 'images/cover-' + article.id + '.jpg'
      return `
        <a class="related-card" href="article.html?id=${article.id}">
          <div class="related-cover">
            <img src="${coverSrc}" alt="${article.title}" loading="lazy">
          </div>
          <div class="related-content">
            <h3>${article.title}</h3>
            <div class="related-date">${article.date || ''}</div>
          </div>
        </a>
      `
    }).join('') +
    '</div>'
}

// ============================================================
//  Reading Progress Bar — tracks how far the reader has
//  scrolled through the article and updates a thin orange
//  bar at the top of the page.
// ============================================================

function updateReadingProgress() {
  const progressBar = document.getElementById('reading-progress')
  if (!progressBar) return

  const articleBody = document.getElementById('article-body')
  if (!articleBody) return

  // Calculate progress based on the article body element
  const rect = articleBody.getBoundingClientRect()
  const articleTop = rect.top + window.scrollY
  const articleHeight = rect.height
  const windowHeight = window.innerHeight

  // How far we've scrolled into the article
  const scrolled = window.scrollY - articleTop + windowHeight
  const progress = Math.max(0, Math.min(100, (scrolled / (articleHeight + windowHeight)) * 100))

  progressBar.style.width = progress + '%'
}

// Only run on article pages
if (document.getElementById('article-container')) {
  window.addEventListener('scroll', updateReadingProgress, { passive: true })
  window.addEventListener('resize', updateReadingProgress)
  window.addEventListener('scroll', toggleBackToTop, { passive: true })
}

// ============================================================
//  Back to Top Button — appears after scrolling down, clicks
//  to smoothly scroll back to the top of the page.
// ============================================================

function toggleBackToTop() {
  const btn = document.getElementById('back-to-top')
  if (!btn) return
  if (window.scrollY > 400) {
    btn.classList.add('visible')
  } else {
    btn.classList.remove('visible')
  }
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ============================================================
//  PDF Download — on the local server, calls the server-side
//  generator. On GitHub Pages (no server), falls back to the
//  browser's print dialog using the print.css stylesheet.
// ============================================================

function downloadPDF() {
  const meta = window.currentArticle
  if (!meta) return

  const btn = document.getElementById('download-btn')
  const originalHTML = btn.innerHTML
  btn.innerHTML = '<span>Preparing...</span>'
  btn.disabled = true

  // Try the local PDF generator first
  const downloadUrl = `http://127.0.0.1:8201/api/pdf?id=${meta.id}`

  // Use fetch to test if the local server is running
  fetch(downloadUrl, { method: 'HEAD', mode: 'no-cors' })
    .then(() => {
      // Local server is running — use iframe download
      let dlFrame = document.getElementById('download-frame')
      if (!dlFrame) {
        dlFrame = document.createElement('iframe')
        dlFrame.id = 'download-frame'
        dlFrame.style.display = 'none'
        document.body.appendChild(dlFrame)
      }
      dlFrame.src = downloadUrl
      setTimeout(() => {
        btn.innerHTML = originalHTML
        btn.disabled = false
      }, 3000)
    })
    .catch(() => {
      // No local server — fall back to browser print
      btn.innerHTML = '<span>Opening print dialog...</span>'
      setTimeout(() => {
        window.print()
        btn.innerHTML = originalHTML
        btn.disabled = false
      }, 500)
    })
}

// Auto-run on article page
if (document.getElementById('article-container')) {
  loadCurrentArticle()
}