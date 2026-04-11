import React from 'react';

// Member 3: Main GUI form
export default function TeamForm({ values, error, result, onFieldChange, onSubmit, isSubmitting }) {
  return (
    <section className="team-panel">
      <form className="team-form" onSubmit={onSubmit}>
        <div className="field-grid">
          <label className="field" htmlFor="total-developers">
            <span>Total number of developers (n)</span>
            <input
              id="total-developers"
              type="number"
              min="1"
              step="1"
              value={values.totalDevelopers}
              onChange={(event) => onFieldChange('totalDevelopers', event.target.value)}
            />
          </label>

          <label className="field" htmlFor="team-size">
            <span>Developers per team (k)</span>
            <input
              id="team-size"
              type="number"
              min="1"
              step="1"
              value={values.teamSize}
              onChange={(event) => onFieldChange('teamSize', event.target.value)}
            />
          </label>
        </div>

        <button className="submit-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Calculating...' : 'Calculate Teams'}
        </button>
      </form>

      {error ? <p className="status-message error">{error}</p> : null}

      <section className="result-card" aria-live="polite">
        <p className="result-label">Sub-teams that can be created</p>
        <p className="result-value">
          {result
            ? `${result.totalTeams} different teams`
            : 'Enter the values above and click Calculate Teams.'}
        </p>

        {result ? (
          <p className="result-formula">
            C({result.totalDevelopers}, {result.teamSize}) = {result.totalTeams}
          </p>
        ) : null}

        <p className="result-note">
          After a valid calculation, the binomial coefficient table appears below on the same page,
          and the final answer is highlighted in a different color.
        </p>
      </section>
    </section>
  );
}
