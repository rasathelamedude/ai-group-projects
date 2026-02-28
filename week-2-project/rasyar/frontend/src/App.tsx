import axios from "axios";
import React, { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:3500/";

interface Board {
  board: number[][];
}

interface SolutionResponse {
  initial_board: number[][];
  steps: number[][][];
  total_cost: number;
  message: string;
}

function App() {
  const [board, setBoard] = useState<number[][] | null>(null);
  const [solution, setSolution] = useState<SolutionResponse | null>(null);
  const [isSolving, setIsSolving] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  const handleGenerate = async () => {
    try {
      const response = await axios.get<Board>(`${API_URL}/generate`);
      setBoard(response.data.board);
      setSolution(null);
      setCurrentStep(0);
      setIsAnimating(false);
      setIsPaused(false);
    } catch (error) {
      console.error("Error generating puzzle:", error);
    }
  };

  const handleSolve = async () => {
    if (!board) return;

    try {
      setIsSolving(true);
      const response = await axios.post<SolutionResponse>(`${API_URL}/solve`, {
        board,
      });
      setSolution(response.data);
      setIsSolving(false);

      // Start animation automatically
      animateSolution(response.data.steps);
    } catch (error) {
      console.error("Error solving puzzle:", error);
      setIsSolving(false);
    }
  };

  const animateSolution = (steps: number[][][]) => {
    setIsAnimating(true);
    setIsPaused(false);
    let stepIndex = 0;

    const interval = setInterval(() => {
      if (stepIndex < steps.length) {
        setBoard(steps[stepIndex]);
        setCurrentStep(stepIndex);
        stepIndex++;
      } else {
        clearInterval(interval);
        setIsAnimating(false);
      }
    }, 500); // 500ms between moves
  };

  const handlePlayPause = () => {
    if (!solution) return;

    if (isPaused) {
      // Resume animation from current step
      const remainingSteps = solution.steps.slice(currentStep);
      animateSolution(remainingSteps);
    } else {
      // Pause (handled by clearing interval - would need refactor for proper pause)
      setIsPaused(true);
    }
  };

  const handleReset = () => {
    if (solution) {
      setBoard(solution.initial_board);
      setCurrentStep(0);
      setIsAnimating(false);
      setIsPaused(false);
    }
  };

  const renderTile = (value: number) => {
    if (value === 0) {
      return <div className="tile empty"></div>;
    }
    return <div className="tile">{value}</div>;
  };

  useEffect(() => {
    function getPuzzle() {
      handleGenerate();
    }

    getPuzzle();
  }, []);

  return (
    <div className="app">
      <header>
        <h1>8-Puzzle Solver</h1>
        <p className="subtitle">Best-First Search Algorithm</p>
      </header>

      <main>
        {/* Puzzle Board */}
        <div className="puzzle-container">
          {board && (
            <div className="puzzle-board">
              {board.map((row, i) => (
                <div key={i} className="puzzle-row">
                  {row.map((tile, j) => (
                    <div key={`${i}-${j}`}>{renderTile(tile)}</div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Status */}
        <div className="status">
          {isSolving && <p className="solving">🔄 Solving puzzle...</p>}
          {solution && !isSolving && (
            <div className="solution-info">
              <p className="success">✅ Solution Found!</p>
              <p className="cost">
                Total Cost: <strong>{solution.total_cost}</strong> moves
              </p>
              <p className="step">
                Step: {currentStep} / {solution.steps.length - 1}
              </p>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="controls">
          <button
            onClick={handleGenerate}
            className="btn btn-secondary"
            disabled={isAnimating || isSolving}
          >
            🔄 New Puzzle
          </button>

          <button
            onClick={handleSolve}
            className="btn btn-primary"
            disabled={!board || isAnimating || isSolving || solution !== null}
          >
            🧠 Solve Puzzle
          </button>
        </div>

        {/* Animation Controls */}
        {solution && (
          <div className="animation-controls">
            <button
              onClick={() => animateSolution(solution.steps)}
              className="btn btn-small"
              disabled={isAnimating}
            >
              ▶️ Replay
            </button>

            <button
              onClick={handleReset}
              className="btn btn-small"
              disabled={isAnimating}
            >
              ⏹️ Reset
            </button>
          </div>
        )}
      </main>

      <footer>
        <p>
          Solution saved to <code>solution.txt</code>
        </p>
      </footer>
    </div>
  );
}

export default App;
