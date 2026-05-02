import { useState, useRef, useCallback } from 'react'

const MODEL_LABELS = { knn: 'kNN', bayesian: 'Bayesian', svm: 'SVM', nn: 'Neural Network' }
const MODEL_TYPES  = { knn: 'k-Nearest Neighbors', bayesian: 'Gaussian Naive Bayes', svm: 'Support Vector Machine', nn: 'Multi-Layer Perceptron' }
const MODEL_COLORS = { knn: '#8b7ca8', bayesian: '#5a8a5e', svm: '#4a7fc1', nn: '#c4622d' }

export default function Prediction({ results }) {
  const models  = results?.models ?? []
  const bestMod = models.length ? models.reduce((a, b) => a.accuracy > b.accuracy ? a : b) : null

  const [active,   setActive]   = useState(null)
  const [preview,  setPreview]  = useState(null)
  const [file,     setFile]     = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [preds,    setPreds]    = useState(null)
  const [error,    setError]    = useState(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef()

  const activeId = active ?? bestMod?.model ?? 'svm'
  const ranked   = [...models].sort((a, b) => b.accuracy - a.accuracy)

  const loadFile = useCallback(f => {
    if (!f?.type.startsWith('image/')) { setError('Please upload a valid image file (JPG, PNG, BMP, WEBP).'); return }
    setError(null); setPreds(null); setFile(f)
    const reader = new FileReader()
    reader.onload = e => setPreview(e.target.result)
    reader.readAsDataURL(f)
  }, [])

  const runPredict = () => {
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    setLoading(true); setError(null)
    fetch('/api/predict', { method: 'POST', body: fd })
      .then(r => r.json())
      .then(d  => { setPreds(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }

  const reset = () => { setFile(null); setPreview(null); setPreds(null); setError(null) }

  const onDrop      = e => { e.preventDefault(); setDragging(false); loadFile(e.dataTransfer.files[0]) }
  const onDragOver  = e => { e.preventDefault(); setDragging(true) }
  const onDragLeave = () => setDragging(false)

  // Build result data for display
  const activePred    = preds?.predictions?.find(p => p.model === activeId)
  const otherPreds    = preds?.predictions?.filter(p => p.model !== activeId) ?? []
  const topProbs      = preds
    ? [...(preds.labels ?? [])].sort((a, b) => (activePred?.probabilities[b] ?? 0) - (activePred?.probabilities[a] ?? 0)).slice(0, 6)
    : []

  return (
    <>
      <div className="section-title">Live Prediction</div>
      <div className="section-sub">
        Run any mammal image through all 4 classifiers at once and compare how each model interprets the photo.
      </div>

      {/* Step 1 */}
      <div className="step-label">
        <span className="step-num-badge">1</span>
        <span className="step-text">Select a model</span>
      </div>

      {ranked.length > 0 ? (
        <div className="model-cards">
          {ranked.map(m => (
            <div
              key={m.model}
              className={`model-card${activeId === m.model ? ' active' : ''}`}
              onClick={() => setActive(m.model)}
            >
              {m.model === bestMod?.model && (
                <div className="model-card-best">Best</div>
              )}
              <div className="model-card-name">{MODEL_LABELS[m.model] ?? m.model}</div>
              <div className="model-card-type">{MODEL_TYPES[m.model] ?? ''}</div>
              <div className="model-card-stat">
                Accuracy <span>{(m.accuracy * 100).toFixed(2)}%</span><br />
                Macro F1 <span>{(m.f1 * 100).toFixed(2)}%</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="spinner-wrap"><div className="spinner" /><span>Loading models…</span></div>
      )}

      <hr className="step-divider" />

      {/* Step 2 */}
      <div className="step-label">
        <span className="step-num-badge">2</span>
        <span className="step-text">Upload a mammal image</span>
      </div>

      <div
        className={`upload-zone${dragging ? ' drag-over' : ''}`}
        onDrop={onDrop} onDragOver={onDragOver} onDragLeave={onDragLeave}
        onClick={() => !preview && inputRef.current.click()}
        style={{ cursor: preview ? 'default' : 'pointer' }}
      >
        <input ref={inputRef} type="file" accept="image/*" style={{ display: 'none' }}
          onChange={e => loadFile(e.target.files[0])} />
        {preview ? (
          <img src={preview} alt="preview" className="upload-preview" />
        ) : (
          <>
            <div className="upload-zone-icon">🖼</div>
            <div className="upload-zone-text">Drop an image here or click to browse</div>
            <div className="upload-zone-hint">
              Accepted formats: JPG, PNG, BMP, WEBP · Best results with brown bear, camel, dolphin, giraffe, horse, kangaroo, koala, polar bear, red panda, zebra
            </div>
          </>
        )}
      </div>

      {error && <div className="alert-error">{error}</div>}

      {/* Step 3 */}
      <div className="step-label" style={{ marginBottom: 14 }}>
        <span className="step-num-badge">3</span>
        <span className="step-text">Run prediction</span>
      </div>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
        <button className="btn-predict" disabled={!file || loading} onClick={runPredict}>
          {loading
            ? <><span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />Running all 4 models…</>
            : file ? 'Predict Mammal Class' : 'Upload an image first'
          }
        </button>
        {preview && !loading && (
          <button className="btn-secondary" onClick={reset}>✕ Clear image</button>
        )}
      </div>

      {/* Results */}
      {preds && !loading && activePred && (
        <>
          <div className="result-header">
            <span className="result-label">Prediction Results</span>
            <span style={{ fontSize: 12, color: 'var(--text-3)' }}>All 4 models ran simultaneously</span>
          </div>

          {/* Featured result for selected model */}
          <div className="result-main">
            <img src={preview} alt="uploaded" className="result-img" />
            <div className="result-main-right">
              <div className="result-model-tag">
                ★ {MODEL_LABELS[activeId]} — your selected model
              </div>
              <div className="result-class">
                {activePred.class.replace(/_/g, ' ')}
              </div>
              <div className="result-conf-text">
                Confidence: <strong>{(activePred.confidence * 100).toFixed(1)}%</strong>
              </div>
              <div className="result-conf-track">
                <div className="result-conf-fill" style={{
                  width: (activePred.confidence * 100).toFixed(1) + '%',
                  background: MODEL_COLORS[activeId] ?? 'var(--green)',
                }} />
              </div>

              <div className="result-bars-title">Top class probabilities</div>
              <div className="pred-conf-list">
                {topProbs.map(label => {
                  const prob = activePred.probabilities[label] ?? 0
                  return (
                    <div className="pred-conf-row" key={label}>
                      <span className="pred-conf-label">{label.replace(/_/g, ' ')}</span>
                      <div className="pred-conf-track">
                        <div className="pred-conf-fill" style={{
                          width: (prob * 100).toFixed(1) + '%',
                          background: label === activePred.class
                            ? (MODEL_COLORS[activeId] ?? 'var(--green)')
                            : 'var(--border-2)',
                        }} />
                      </div>
                      <span className="pred-conf-pct">{(prob * 100).toFixed(1)}%</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Other models summary */}
          {otherPreds.length > 0 && (
            <>
              <div className="result-others-title">Other models predicted</div>
              <div className="result-others">
                {otherPreds.map(p => (
                  <div className="result-other-card" key={p.model}
                    style={{ borderLeftColor: MODEL_COLORS[p.model], borderLeftWidth: 3 }}>
                    <div className="result-other-model">
                      <span className="result-other-dot" style={{ background: MODEL_COLORS[p.model] }} />
                      {MODEL_LABELS[p.model] ?? p.model}
                    </div>
                    <div className="result-other-class">{p.class.replace(/_/g, ' ')}</div>
                    <div className="result-other-conf">{(p.confidence * 100).toFixed(1)}% confidence</div>
                  </div>
                ))}
              </div>

              {/* Agreement indicator */}
              {(() => {
                const allPredictions = preds.predictions.map(p => p.class)
                const agree = allPredictions.every(c => c === allPredictions[0])
                const uniqueClasses = [...new Set(allPredictions)]
                return (
                  <div style={{ marginTop: 12, padding: '8px 12px', borderRadius: 8, fontSize: 12,
                    background: agree ? 'rgba(61,107,94,.08)' : 'rgba(196,98,45,.08)',
                    color: agree ? 'var(--green)' : 'var(--orange)', fontWeight: 500 }}>
                    {agree
                      ? '✓ All 4 models agree — high confidence in the prediction'
                      : `⚡ Models disagree — ${uniqueClasses.length} different predictions (${uniqueClasses.map(c => c.replace(/_/g,' ')).join(', ')})`
                    }
                  </div>
                )
              })()}
            </>
          )}
        </>
      )}
    </>
  )
}
