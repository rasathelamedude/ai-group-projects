import React, { useState } from 'react';
import TeamForm from './members/member3/TeamForm.jsx';
import BinomialPopup from './members/member4/BinomialPopup.jsx';

const defaultValues = {
  totalDevelopers: '10',
  teamSize: '4',
};

const browserHost = window.location.hostname || '127.0.0.1';
const backendBaseUrl = import.meta.env.VITE_API_BASE_URL || `http://${browserHost}:8000`;
const calculationEndpoint = `${backendBaseUrl}/api/calculate`;

export default function App() {
  const [formValues, setFormValues] = useState(defaultValues);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [popupData, setPopupData] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFieldChange = (field, value) => {
    setFormValues((currentValues) => ({
      ...currentValues,
      [field]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setIsSubmitting(true);

    try {
      const response = await fetch(calculationEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          total_developers: formValues.totalDevelopers,
          team_size: formValues.teamSize,
        }),
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || 'Could not calculate the project teams.');
      }

      const nextResult = {
        totalDevelopers: payload.total_developers,
        teamSize: payload.team_size,
        totalTeams: payload.total_teams,
      };

      setError('');
      setResult(nextResult);
      setPopupData({
        ...nextResult,
        table: payload.table,
      });
    } catch (error) {
      const message =
        error instanceof Error && error.message === 'Failed to fetch'
          ? 'Could not connect to the Python backend. Start FastAPI on port 8000 and try again.'
          : error instanceof Error
            ? error.message
            : 'Could not calculate the project teams.';

      setError(message);
      setResult(null);
      setPopupData(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="app-shell">
        <div className="app-glow app-glow-left" />
        <div className="app-glow app-glow-right" />

        <main className="app-card">
          <header className="hero">
            <p className="hero-kicker">Project Team Calculator</p>
            <h1>Forming Project Teams</h1>
            <p className="hero-copy">
              Enter the total developers and the developers required per team. The answer appears
              on this page, and the binomial coefficient table appears below the result after a
              valid calculation.
            </p>
          </header>

          <TeamForm
            values={formValues}
            error={error}
            result={result}
            onFieldChange={handleFieldChange}
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
          />

          <BinomialPopup data={popupData} />
        </main>
      </div>
    </>
  );
}
