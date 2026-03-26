import React from 'react';
import './SubjectFilter.css';

const SubjectFilter = ({ value, onChange, subjects }) => {
  return (
    <label className="filter-field">
      Subject
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">All Subjects</option>
        {subjects.map((subject) => (
          <option key={subject} value={subject}>
            {subject}
          </option>
        ))}
      </select>
    </label>
  );
};

export default SubjectFilter;
