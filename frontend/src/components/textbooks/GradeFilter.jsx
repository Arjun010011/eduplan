import React from 'react';
import './GradeFilter.css';

const GradeFilter = ({ value, onChange }) => {
  return (
    <label className="filter-field">
      Grade
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">All Grades</option>
        {Array.from({ length: 12 }, (_, i) => i + 1).map((grade) => (
          <option key={grade} value={grade}>
            {grade}
          </option>
        ))}
      </select>
    </label>
  );
};

export default GradeFilter;
