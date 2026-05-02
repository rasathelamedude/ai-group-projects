import { useState } from 'react'

const MODEL_LABELS = { knn: 'kNN', bayesian: 'Bayesian', svm: 'SVM', nn: 'Neural Network' }
const BAR_COLORS   = { svm: '#4a7fc1', nn: '#c4622d', bayesian: '#5a8a5e', knn: '#8b7ca8' }
const TICK_VALS    = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
const CHART_H      = 200

const METRIC_INFO = {
  accuracy:  { label: 'Accuracy',        hint: 'Overall % correct predictions' },
  precision: { label: 'Macro Precision', hint: 'Avg precision across all classes' },
  recall:    { label: 'Macro Recall',    hint: 'Avg recall across all classes'    },
  f1:        { label: 'Macro F1',        hint: 'Harmonic mean of precision & recall' },
}

/* ── Bar chart ─────────────────────────────────────────────────────────── */
function BarChart({ models }) {
  const ranked = [...models].sort((a, b) => b.accuracy - a.accuracy)
  return (
    <div>
      <div style={{ fontSize: 12, color: 'var(--text)', textAlign: 'center', marginBottom: 12, fontWeight: 600 }}>
        Accuracy Comparison Across Trained Models
      </div>
      <div style={{ display: 'flex' }}>
        {/* y-axis */}
        <div style={{ position: 'relative', width: 32, height: CHART_H, flexShrink: 0 }}>
          <div style={{ position: 'absolute', left: -8, top: '50%', transform: 'translateY(-50%) rotate(-90deg)', fontSize: 10, color: 'var(--text-3)', whiteSpace: 'nowrap' }}>
            Accuracy
          </div>
          {TICK_VALS.map(t => (
            <div key={t} style={{ position: 'absolute', right: 3, bottom: `${t * 100}%`, transform: 'translateY(50%)', fontSize: 9.5, color: 'var(--text-3)', lineHeight: 1 }}>
              {t.toFixed(1)}
            </div>
          ))}
        </div>
        {/* body */}
        <div style={{ position: 'relative', flex: 1, height: CHART_H, borderLeft: '1.5px solid #bbb', borderBottom: '1.5px solid #bbb' }}>
          {TICK_VALS.slice(1).map(t => (
            <div key={t} style={{ position: 'absolute', left: 0, right: 0, bottom: `${t * 100}%`, borderTop: '1px solid rgba(0,0,0,.07)' }} />
          ))}
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'flex-end', padding: '0 12px', gap: 6 }}>
            {ranked.map(m => (
              <div key={m.model} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end', gap: 3, height: '100%' }}>
                <span style={{ fontSize: 9.5, color: 'var(--text-2)', fontWeight: 600 }}>{(m.accuracy * 100).toFixed(1)}%</span>
                <div style={{ width: '70%', height: Math.round(m.accuracy * CHART_H), background: BAR_COLORS[m.model] ?? '#888', borderRadius: '2px 2px 0 0' }} />
              </div>
            ))}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', paddingLeft: 34, paddingTop: 7, gap: 6 }}>
        {ranked.map(m => (
          <div key={m.model} style={{ flex: 1, textAlign: 'center', fontSize: 10.5, color: 'var(--text-2)' }}>
            <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: BAR_COLORS[m.model], marginRight: 4, verticalAlign: 'middle' }} />
            {MODEL_LABELS[m.model] ?? m.model}
          </div>
        ))}
      </div>
    </div>
  )
}

/* ── Dataset snapshot ──────────────────────────────────────────────────── */
function DatasetSnapshot({ dataset }) {
  if (!dataset) return null
  const { label_names: labels = [], counts = {}, total = 1, n_train, n_test } = dataset
  return (
    <div>
      <div className="snapshot-title">Dataset Snapshot</div>
      <table className="snapshot-table">
        <tbody>
          {labels.map(l => (
            <tr key={l}>
              <td>{l.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</td>
              <td>
                <strong>{counts[l] ?? 0}</strong>
                <span style={{ fontSize: 10, color: 'var(--text-3)', marginLeft: 4 }}>
                  {total > 0 ? ((counts[l] / total) * 100).toFixed(0) + '%' : ''}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 8 }}>
        Total: <strong style={{ color: 'var(--text-2)' }}>{total.toLocaleString()}</strong> · {n_train} train / {n_test} test
      </div>
    </div>
  )
}

/* ── Metrics table ─────────────────────────────────────────────────────── */
function MetricsTable({ models }) {
  const ranked  = [...models].sort((a, b) => b.accuracy - a.accuracy)
  const metrics = ['accuracy', 'precision', 'recall', 'f1']
  const bestVals = {}
  metrics.forEach(k => { bestVals[k] = Math.max(...models.map(m => m[k])) })
  const winner = ranked[0]?.model

  return (
    <>
      <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 10, display: 'flex', gap: 14, flexWrap: 'wrap' }}>
        {metrics.map(k => (
          <span key={k}><strong style={{ color: 'var(--text-2)' }}>{METRIC_INFO[k].label}:</strong> {METRIC_INFO[k].hint}</span>
        ))}
      </div>
      <div className="table-wrap">
        <table className="metrics-table">
          <thead>
            <tr>
              <th>Model</th>
              {metrics.map(k => (
                <th key={k}>{METRIC_INFO[k].label}<small>{METRIC_INFO[k].hint}</small></th>
              ))}
              <th>Train Time</th>
            </tr>
          </thead>
          <tbody>
            {ranked.map(m => (
              <tr key={m.model} className={m.model === winner ? 'winner-row' : ''}>
                <td>{MODEL_LABELS[m.model] ?? m.model}</td>
                {metrics.map(k => (
                  <td key={k} className={m[k] === bestVals[k] ? 'td-best' : ''}>
                    {m[k].toFixed(4)}{m[k] === bestVals[k] && <span style={{ marginLeft: 3, fontSize: 10 }}>★</span>}
                  </td>
                ))}
                <td style={{ color: 'var(--text-3)' }}>{m.train_time != null ? m.train_time.toFixed(2) + 's' : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 8 }}>
        ★ Best value per metric · First row = overall winner · Evaluated on held-out test set (20% of images)
      </div>
    </>
  )
}

/* ── Per-class F1 heatmap ──────────────────────────────────────────────── */
function lerp(a, b, t) { return Math.round(a + (b - a) * t) }
function greenScale(f1) {
  const t = Math.min(1, Math.max(0, f1))
  return `rgb(${lerp(248, 61, t)}, ${lerp(250, 107, t)}, ${lerp(248, 94, t)})`
}
function greenText(f1) { return f1 > 0.52 ? '#fff' : 'var(--text)' }

function PerClassHeatmap({ models }) {
  const labels = models[0]?.label_names ?? []
  const cols   = ['svm', 'nn', 'bayesian', 'knn']
    .map(id => models.find(m => m.model === id))
    .filter(Boolean)

  const TH = { padding: '8px 10px', fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--text-3)', borderBottom: '1.5px solid var(--border)', textAlign: 'center' }

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <span style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text)' }}>F1 Score per Animal Class</span>
        <span style={{ fontSize: 12, color: 'var(--text-3)', marginLeft: 10 }}>
          Darker green = the model classifies that animal well. Outlined cell = best model for that animal.
        </span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 380 }}>
          <thead>
            <tr>
              <th style={{ ...TH, textAlign: 'left' }}>Animal</th>
              {cols.map(m => (
                <th key={m.model} style={TH}>
                  <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: BAR_COLORS[m.model], marginRight: 5, verticalAlign: 'middle' }} />
                  {MODEL_LABELS[m.model]}
                </th>
              ))}
              <th style={{ ...TH, textAlign: 'left' }}>Test Images</th>
            </tr>
          </thead>
          <tbody>
            {labels.map(l => {
              const f1s    = cols.map(m => m.per_class?.[l]?.f1 ?? 0)
              const bestF1 = Math.max(...f1s)
              const support = cols[0]?.per_class?.[l]?.support ?? 0
              return (
                <tr key={l}>
                  <td style={{ padding: '7px 10px', fontSize: 13, color: 'var(--text-2)', textTransform: 'capitalize', borderBottom: '1px solid var(--border)', fontWeight: 500 }}>
                    {l.replace(/_/g, ' ')}
                  </td>
                  {cols.map((m, ci) => {
                    const f1 = m.per_class?.[l]?.f1 ?? 0
                    const isBest = f1 === bestF1 && f1 > 0
                    return (
                      <td key={m.model}
                        style={{
                          padding: '7px 10px', textAlign: 'center', fontSize: 13, fontWeight: 700,
                          background: greenScale(f1), color: greenText(f1),
                          borderBottom: '1px solid rgba(255,255,255,.25)',
                          outline: isBest ? '2px solid rgba(61,107,94,.6)' : 'none',
                          outlineOffset: -2,
                        }}
                        title={`${MODEL_LABELS[m.model]} on "${l.replace(/_/g, ' ')}": F1 = ${(f1*100).toFixed(1)}%  |  precision = ${((m.per_class?.[l]?.precision ?? 0)*100).toFixed(1)}%  |  recall = ${((m.per_class?.[l]?.recall ?? 0)*100).toFixed(1)}%`}
                      >
                        {(f1 * 100).toFixed(0)}%
                      </td>
                    )
                  })}
                  <td style={{ padding: '7px 10px', fontSize: 12, color: 'var(--text-3)', borderBottom: '1px solid var(--border)' }}>
                    {support} images
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 10 }}>
        Hover any cell for precision &amp; recall details · Outlined = best-performing model for that animal
      </div>
    </div>
  )
}

/* ── NN Loss Curve ─────────────────────────────────────────────────────── */
function LossCurve({ models }) {
  const nnModel = models.find(m => m.model === 'nn')
  const losses  = nnModel?.loss_curve ?? []

  if (losses.length < 2) {
    return (
      <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-3)' }}>
        No training curve data is available for the Neural Network model.
      </div>
    )
  }

  const W = 560, H = 230
  const pad = { t: 20, r: 24, b: 44, l: 58 }
  const pw  = W - pad.l - pad.r
  const ph  = H - pad.t - pad.b

  const minL   = Math.min(...losses)
  const maxL   = Math.max(...losses)
  const range  = maxL - minL || 1
  const sx = i => pad.l + (i / (losses.length - 1)) * pw
  const sy = v => pad.t + (1 - (v - minL) / range) * ph

  const pathD = losses.map((v, i) => `${i === 0 ? 'M' : 'L'}${sx(i).toFixed(1)},${sy(v).toFixed(1)}`).join(' ')

  const yTicks = 5
  const yVals  = Array.from({ length: yTicks + 1 }, (_, i) => minL + (range / yTicks) * i)

  const xStep  = Math.max(1, Math.ceil(losses.length / 7))
  const xIdxs  = []
  for (let i = 0; i < losses.length; i += xStep) xIdxs.push(i)
  if (xIdxs[xIdxs.length - 1] !== losses.length - 1) xIdxs.push(losses.length - 1)

  const reduction = ((1 - losses[losses.length - 1] / losses[0]) * 100).toFixed(1)

  return (
    <div>
      <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text)', textAlign: 'center', marginBottom: 4 }}>
        Neural Network — Training Loss Curve
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-3)', textAlign: 'center', marginBottom: 14 }}>
        Loss dropped from <strong style={{ color: 'var(--text-2)' }}>{losses[0].toFixed(3)}</strong> to{' '}
        <strong style={{ color: 'var(--green)' }}>{losses[losses.length - 1].toFixed(3)}</strong> over{' '}
        {losses.length} iterations — a {reduction}% reduction
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', maxWidth: W, display: 'block', margin: '0 auto', overflow: 'visible' }}>
        {/* y gridlines + tick labels */}
        {yVals.map((v, i) => (
          <g key={i}>
            <line x1={pad.l} x2={pad.l + pw} y1={sy(v).toFixed(1)} y2={sy(v).toFixed(1)} stroke="rgba(0,0,0,.07)" strokeWidth="1" />
            <text x={pad.l - 6} y={sy(v)} textAnchor="end" dominantBaseline="middle" fontSize="10" fill="var(--text-3)">
              {v.toFixed(2)}
            </text>
          </g>
        ))}

        {/* x gridlines + tick labels */}
        {xIdxs.map(i => (
          <g key={i}>
            <line x1={sx(i).toFixed(1)} x2={sx(i).toFixed(1)} y1={pad.t} y2={pad.t + ph} stroke="rgba(0,0,0,.06)" strokeWidth="1" />
            <text x={sx(i)} y={pad.t + ph + 14} textAnchor="middle" fontSize="10" fill="var(--text-3)">{i + 1}</text>
          </g>
        ))}

        {/* axes */}
        <line x1={pad.l} x2={pad.l} y1={pad.t} y2={pad.t + ph} stroke="#bbb" strokeWidth="1.5" />
        <line x1={pad.l} x2={pad.l + pw} y1={pad.t + ph} y2={pad.t + ph} stroke="#bbb" strokeWidth="1.5" />

        {/* gradient fill under line */}
        <defs>
          <linearGradient id="lossGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#c4622d" stopOpacity="0.18" />
            <stop offset="100%" stopColor="#c4622d" stopOpacity="0.01" />
          </linearGradient>
        </defs>
        <path
          d={`${pathD} L${sx(losses.length - 1).toFixed(1)},${pad.t + ph} L${pad.l},${pad.t + ph} Z`}
          fill="url(#lossGrad)"
        />

        {/* loss line */}
        <path d={pathD} fill="none" stroke="#c4622d" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />

        {/* final point dot */}
        <circle cx={sx(losses.length - 1)} cy={sy(losses[losses.length - 1])} r="4" fill="#c4622d" />

        {/* axis labels */}
        <text x={pad.l + pw / 2} y={H - 2} textAnchor="middle" fontSize="10.5" fill="var(--text-3)">Training Iteration</text>
        <text x={14} y={pad.t + ph / 2} textAnchor="middle" fontSize="10.5" fill="var(--text-3)" transform={`rotate(-90, 14, ${pad.t + ph / 2})`}>Loss</text>
      </svg>

      <div style={{ marginTop: 16, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {[
          { label: 'Architecture', value: '256 → 128 → 64 → 10', hint: 'Hidden layer neurons' },
          { label: 'Solver', value: 'Adam', hint: 'Adaptive learning rate' },
          { label: 'Early Stopping', value: 'Yes (n=15)', hint: 'Stopped before max_iter' },
        ].map(info => (
          <div key={info.label} style={{ background: 'var(--surface-2)', borderRadius: 8, padding: '10px 14px', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-3)', marginBottom: 3 }}>{info.label}</div>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)', marginBottom: 1 }}>{info.value}</div>
            <div style={{ fontSize: 11, color: 'var(--text-3)' }}>{info.hint}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ── Insight callout ───────────────────────────────────────────────────── */
function InsightCallout({ models }) {
  if (!models.length) return null
  const ranked = [...models].sort((a, b) => b.accuracy - a.accuracy)
  const best   = ranked[0]
  const worst  = ranked[ranked.length - 1]

  // Find most-confused pair (off-diagonal max) in best model
  const cm     = best.confusion_matrix
  const labels = best.label_names
  let maxVal = 0, fromLbl = '', toLbl = ''
  cm.forEach((row, r) => row.forEach((v, c) => {
    if (r !== c && v > maxVal) { maxVal = v; fromLbl = labels[r]; toLbl = labels[c] }
  }))

  return (
    <div style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10, padding: '14px 18px', marginBottom: 24, display: 'flex', gap: 20, flexWrap: 'wrap' }}>
      <div style={{ flex: 1, minWidth: 200 }}>
        <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.09em', color: 'var(--green)', marginBottom: 4 }}>Top Performer</div>
        <div style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text)' }}>
          {MODEL_LABELS[best.model]} — {(best.accuracy * 100).toFixed(1)}% accuracy
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>
          {((best.accuracy - worst.accuracy) * 100).toFixed(1)}% ahead of {MODEL_LABELS[worst.model]} ({(worst.accuracy * 100).toFixed(1)}%)
        </div>
      </div>
      {fromLbl && (
        <div style={{ flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.09em', color: 'var(--orange)', marginBottom: 4 }}>Hardest Confusion ({MODEL_LABELS[best.model]})</div>
          <div style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text)' }}>
            {fromLbl.replace(/_/g, ' ')} → {toLbl.replace(/_/g, ' ')}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>
            {maxVal} test images misclassified as {toLbl.replace(/_/g, ' ')}
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Main export ───────────────────────────────────────────────────────── */
const TABS = [
  { id: 'overview',  label: 'Accuracy Overview' },
  { id: 'perclass',  label: 'Per Animal F1' },
  { id: 'training',  label: 'NN Training Curve' },
]

export default function Comparison({ results, dataset }) {
  const [tab, setTab] = useState('overview')

  if (!results) return <div className="spinner-wrap"><div className="spinner" /><span>Loading results…</span></div>
  const models = results.models ?? []

  return (
    <>
      <div className="section-title">Model Comparison</div>
      <div className="section-sub">
        All metrics come from the Python evaluation pipeline — the UI only visualises the saved results.
        Each model was trained on the same HOG + color histogram features, PCA-reduced to 150 dimensions.
      </div>

      <InsightCallout models={models} />

      {/* Tabs */}
      <div className="comp-tabs">
        {TABS.map(t => (
          <button key={t.id} className={`comp-tab-btn${tab === t.id ? ' active' : ''}`} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview */}
      {tab === 'overview' && (
        <>
          <div className="comparison-top">
            <BarChart models={models} />
            <DatasetSnapshot dataset={dataset} />
          </div>
          <MetricsTable models={models} />
        </>
      )}

      {/* Tab 2: Per-class */}
      {tab === 'perclass' && <PerClassHeatmap models={models} />}

      {/* Tab 3: NN training curve */}
      {tab === 'training' && <LossCurve models={models} />}
    </>
  )
}
