const MODEL_LABELS  = { knn: 'kNN', bayesian: 'Bayesian', svm: 'SVM', nn: 'Neural Network' }
const DISPLAY_ORDER = ['svm', 'nn', 'bayesian', 'knn']

function lerp(a, b, t) { return Math.round(a + (b - a) * t) }

function blueScale(t) {
  if (t < 0.25) { const s = t / 0.25; return `rgb(${lerp(247,198,s)},${lerp(251,219,s)},${lerp(255,239,s)})` }
  if (t < 0.50) { const s = (t-.25)/.25; return `rgb(${lerp(198,107,s)},${lerp(219,174,s)},${lerp(239,214,s)})` }
  if (t < 0.75) { const s = (t-.50)/.25; return `rgb(${lerp(107,33,s)},${lerp(174,113,s)},${lerp(214,181,s)})` }
  const s = (t-.75)/.25
  return `rgb(${lerp(33,8,s)},${lerp(113,48,s)},${lerp(181,107,s)})`
}

function Heatmap({ label_names, cm, modelId }) {
  const n       = label_names.length
  const maxVal  = Math.max(...cm.flat())
  const cellSz  = 26
  const labelW  = 58
  const cbStops = [maxVal, Math.round(maxVal*.75), Math.round(maxVal*.5), Math.round(maxVal*.25), 0]

  const textColor = val => (maxVal > 0 && val / maxVal > 0.55) ? '#fff' : '#1a1a14'

  return (
    <div className="heatmap">
      <div className="heatmap-title">{MODEL_LABELS[modelId] ?? modelId} Confusion Matrix</div>

      <div className="heatmap-body">
        {/* True Label axis */}
        <div className="heatmap-ylabel" style={{ height: cellSz * n }}>True Label</div>

        {/* Row labels + grid */}
        <div>
          <div style={{ display: 'flex' }}>
            <div className="heatmap-row-labels" style={{ width: labelW }}>
              {label_names.map(l => (
                <div key={l} className="heatmap-rlabel" style={{ height: cellSz }}>
                  {l.replace(/_/g, ' ')}
                </div>
              ))}
            </div>

            <div className="heatmap-grid"
              style={{ gridTemplateColumns: `repeat(${n}, ${cellSz}px)`, gridTemplateRows: `repeat(${n}, ${cellSz}px)` }}>
              {cm.map((row, ri) =>
                row.map((val, ci) => {
                  const t = maxVal > 0 ? val / maxVal : 0
                  const isDiag = ri === ci
                  return (
                    <div
                      key={`${ri}-${ci}`}
                      className={`heatmap-cell${isDiag ? ' diag' : ''}`}
                      style={{ width: cellSz, height: cellSz, background: blueScale(t), color: textColor(val) }}
                      title={`True: ${label_names[ri]}  →  Predicted: ${label_names[ci]}  (${val} images)`}
                    >
                      {val}
                    </div>
                  )
                })
              )}
            </div>
          </div>

          {/* Column labels */}
          <div style={{ display: 'flex', paddingLeft: labelW }}>
            {label_names.map(l => (
              <div key={l} className="heatmap-clabel" style={{ width: cellSz, height: 50 }}>
                {l.replace(/_/g, ' ')}
              </div>
            ))}
          </div>

          <div className="heatmap-xlabel" style={{ paddingLeft: labelW }}>Predicted Label</div>
        </div>

        {/* Colorbar */}
        <div style={{ display: 'flex', paddingLeft: 6 }}>
          <div className="heatmap-colorbar" style={{ height: cellSz * n }} />
          <div className="heatmap-cb-labels" style={{ height: cellSz * n }}>
            {cbStops.map((v, i) => <span key={i}>{v}</span>)}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Matrices({ results }) {
  if (!results) return null
  const models = results.models ?? []
  if (!models.length) return null

  const ordered   = DISPLAY_ORDER.map(id => models.find(m => m.model === id)).filter(Boolean)
  const remaining = models.filter(m => !DISPLAY_ORDER.includes(m.model))
  const all = [...ordered, ...remaining]

  return (
    <div className="matrices-section">
      {/* Section header */}
      <div className="matrices-header">
        <div className="matrices-header-title">Confusion Matrices</div>
        <div className="matrices-header-sub">
          Visualises where each model succeeds and where it confuses similar-looking animals.
        </div>
      </div>

      {/* How to read legend */}
      <div className="matrices-legend">
        <div className="legend-item">
          <div className="legend-swatch" style={{ background: 'rgb(8,48,107)', outline: '2px solid rgba(61,107,94,.55)', outlineOffset: -2 }} />
          <span>Diagonal cells = correct predictions (the model predicted the right class)</span>
        </div>
        <div className="legend-item">
          <div className="legend-swatch" style={{ background: 'rgb(107,174,214)' }} />
          <span>Off-diagonal = misclassifications (darker = more errors)</span>
        </div>
        <div className="legend-item">
          <div className="legend-swatch" style={{ background: 'rgb(247,251,255)', border: '1px solid #ddd' }} />
          <span>White/light = zero or very few images</span>
        </div>
      </div>

      <div className="matrices-grid">
        {all.map(m => (
          <div className="matrix-card" key={m.model}>
            <div className="matrix-card-head">
              <span className="matrix-card-name">{MODEL_LABELS[m.model] ?? m.model}</span>
              <span className="badge-ready">UI-ready</span>
            </div>
            <div className="matrix-card-acc">
              Test accuracy: <strong>{(m.accuracy * 100).toFixed(2)}%</strong>
              <span style={{ marginLeft: 10, color: 'var(--text-3)', fontSize: 11 }}>
                (hover any cell to see the exact count)
              </span>
            </div>
            <Heatmap label_names={m.label_names} cm={m.confusion_matrix} modelId={m.model} />
          </div>
        ))}
      </div>
    </div>
  )
}
