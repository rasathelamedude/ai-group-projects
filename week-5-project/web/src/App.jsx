import { useState, useEffect } from 'react'
import Hero from './sections/Hero'
import Prediction from './sections/Prediction'
import Comparison from './sections/Comparison'
import Matrices from './sections/Matrices'

function ScrollToTop() {
  const [show, setShow] = useState(false)
  useEffect(() => {
    const fn = () => setShow(window.scrollY > 500)
    window.addEventListener('scroll', fn, { passive: true })
    return () => window.removeEventListener('scroll', fn)
  }, [])
  if (!show) return null
  return (
    <button
      className="scroll-top-btn"
      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      title="Back to top"
    >
      ↑
    </button>
  )
}

export default function App() {
  const [results, setResults] = useState(null)
  const [dataset, setDataset] = useState(null)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    Promise.all([
      fetch('/api/results').then(r => r.json()),
      fetch('/api/dataset').then(r => r.json()),
    ])
      .then(([res, ds]) => { setResults(res); setDataset(ds) })
      .catch(err => setError(err.message))
  }, [])

  // Scroll-reveal: add .visible to .reveal elements as they enter view
  useEffect(() => {
    const obs = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible') }),
      { threshold: 0.08 }
    )
    const els = document.querySelectorAll('.reveal')
    els.forEach(el => obs.observe(el))
    return () => obs.disconnect()
  }, [results])   // re-run once data arrives and DOM updates

  return (
    <>
      <nav className="sticky-nav">
        <a href="#overview">Overview</a>
        <a href="#predict">Live Prediction</a>
        <a href="#compare">Model Comparison</a>
        <a href="#matrices">Confusion Matrices</a>
      </nav>

      <div className="page-wrap">
        <div className="container">
          {error && (
            <div className="alert-error">
              API error: {error} — make sure the FastAPI server is running on port 8000.
            </div>
          )}

          <div id="overview" className="reveal">
            <Hero results={results} dataset={dataset} />
          </div>

          <div id="predict" className="reveal">
            <section className="section">
              <Prediction results={results} />
            </section>
          </div>

          <div id="compare" className="reveal">
            <section className="section">
              <Comparison results={results} dataset={dataset} />
            </section>
          </div>

          <div id="matrices" className="reveal">
            <Matrices results={results} />
          </div>
        </div>
      </div>

      <ScrollToTop />
    </>
  )
}
