import { useState, useEffect } from 'react'

const MODEL_LABELS = { knn: 'kNN', bayesian: 'Bayesian', svm: 'SVM', nn: 'Neural Network' }

const HOW_STEPS = [
  {
    num: '01',
    title: 'Select a Model',
    desc: 'Pick one of 4 classifiers — SVM, Neural Network, Bayesian, or kNN. Each uses a different algorithm trained on identical features.',
  },
  {
    num: '02',
    title: 'Upload an Image',
    desc: 'Drop any mammal photo from your computer. Best results with clear, single-animal images from the 10 training classes.',
  },
  {
    num: '03',
    title: 'Compare Results',
    desc: 'All 4 models run simultaneously. See predictions, confidence scores, and whether the models agree or disagree.',
  },
]

function AnimatedNum({ target, duration = 1400 }) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    if (!target && target !== 0) return
    const n = Number(target)
    if (isNaN(n)) { setVal(target); return }
    const start = performance.now()
    const tick  = now => {
      const t = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - t, 3)
      setVal(Math.round(eased * n))
      if (t < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [target, duration])
  return <>{typeof val === 'number' ? val.toLocaleString() : val}</>
}

export default function Hero({ results, dataset }) {
  const models = results?.models ?? []
  const best   = models.length ? models.reduce((a, b) => (a.accuracy > b.accuracy ? a : b)) : null

  return (
    <div className="hero">
      <div className="hero-layout">
        <div className="hero-left">
          <div className="hero-label">Final Project Demo UI</div>
          <h1 className="hero-title">
            Multi-Model<br />
            Mammal<br />
            Classification<br />
            System
          </h1>
          <p className="hero-desc">
            Upload a mammal image, choose one of the trained Python models, and compare
            live predictions against saved evaluation metrics. No internet or pretrained
            weights required — everything runs locally on your machine.
          </p>
          <div className="hero-tags">
            <span className="hero-tag">No pretrained models</span>
            <span className="hero-tag">HOG + Color features</span>
            <span className="hero-tag">Python backend</span>
            <span className="hero-tag">React UI</span>
          </div>
        </div>

        <div className="hero-stats">
          <div className="stat-badge">
            <span className="stat-badge-label">Best Model</span>
            <span className="stat-badge-value">
              {best ? (MODEL_LABELS[best.model] ?? best.model) : '—'}
            </span>
            {best && (
              <span className="stat-badge-sub">
                <AnimatedNum target={parseFloat((best.accuracy * 100).toFixed(1))} duration={1200} />% accuracy
              </span>
            )}
          </div>

          <div className="stat-badge">
            <span className="stat-badge-label">Animal Classes</span>
            <span className="stat-badge-value">
              <AnimatedNum target={dataset?.n_classes} />
            </span>
            <span className="stat-badge-sub">
              {dataset?.label_names
                ? dataset.label_names.slice(0, 3).map(l => l.replace(/_/g, ' ')).join(', ') + '…'
                : ''}
            </span>
          </div>

          <div className="stat-badge">
            <span className="stat-badge-label">Dataset Size</span>
            <span className="stat-badge-value">
              <AnimatedNum target={dataset?.total} />
            </span>
            <span className="stat-badge-sub">
              {dataset ? `${dataset.n_train.toLocaleString()} train · ${dataset.n_test} test` : ''}
            </span>
          </div>
        </div>
      </div>

      {/* How it works */}
      <div className="how-title">How it works</div>
      <div className="how-steps">
        {HOW_STEPS.map(s => (
          <div className="how-step" key={s.num}>
            <div className="how-step-num">{s.num}</div>
            <div className="how-step-title">{s.title}</div>
            <div className="how-step-desc">{s.desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
