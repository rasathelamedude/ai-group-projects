import React from 'react';

// Member 4: Table board + colored result
export default function BinomialPopup({ data }) {
  if (!data) {
    return null;
  }

  const { totalDevelopers, teamSize, totalTeams, table } = data;
  const columns = Array.from({ length: totalDevelopers + 1 }, (_, column) => column);

  return (
    <section className="table-card" aria-live="polite">
      <p className="table-label">Binomial coefficient table</p>
      <h2 className="table-heading">How the answer was calculated</h2>
      <p className="table-formula">
        C({totalDevelopers}, {teamSize}) = {totalTeams}
      </p>
      <p className="table-legend">The orange cell is the final answer.</p>

      <div className="table-wrap">
        <table className="binomial-table">
          <thead>
            <tr>
              <th scope="col">n \ k</th>
              {columns.map((column) => (
                <th key={column} scope="col">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <th className="row-heading" scope="row">
                  {rowIndex}
                </th>

                {columns.map((column) => {
                  const isEmpty = column > rowIndex;
                  const isSolution = rowIndex === totalDevelopers && column === teamSize;
                  const className = [
                    'binomial-cell',
                    isEmpty ? 'binomial-empty' : '',
                    isSolution ? 'binomial-solution' : '',
                  ]
                    .filter(Boolean)
                    .join(' ');

                  return (
                    <td key={column} className={className}>
                      {isEmpty ? '' : row[column]}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
