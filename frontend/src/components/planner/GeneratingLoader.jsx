import React from 'react';
import './GeneratingLoader.css';

const GeneratingLoader = () => {
  return (
    <div className="generating-loader">
      <div className="spinner" />
      <p>Claude is crafting your plan…</p>
    </div>
  );
};

export default GeneratingLoader;
