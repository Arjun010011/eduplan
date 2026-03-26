import React from 'react';
import './PlanResult.css';

const PlanResult = ({ result }) => {
  return (
    <div className="plan-result">
      <div className="success-banner">🎉 Your course plan is ready!</div>
      <a className="download" href={result.pdf_url} target="_blank" rel="noreferrer">
        Download PDF
      </a>
      <details>
        <summary>View LaTeX Source</summary>
        <pre>
          <code>{result.latex_output}</code>
        </pre>
      </details>
    </div>
  );
};

export default PlanResult;
