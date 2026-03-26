import React, { useMemo } from 'react';
import './PlannerForm.css';

const SUBJECTS_BY_BOARD = {
  CBSE: ['Maths', 'Science', 'English', 'Social Studies', 'Hindi'],
  ICSE: ['Maths', 'Physics', 'Chemistry', 'Biology', 'English', 'History'],
  KA_STATE: ['Maths', 'Science', 'English', 'Social Studies', 'Kannada'],
};

const PlannerForm = ({ values, onChange, onSubmit, submitting }) => {
  const subjects = useMemo(() => SUBJECTS_BY_BOARD[values.board] || [], [values.board]);

  return (
    <form className="planner-form" onSubmit={onSubmit}>
      <label>
        Teacher Name
        <input
          type="text"
          value={values.teacher_name}
          onChange={(event) => onChange('teacher_name', event.target.value)}
          required
        />
      </label>

      <label>
        Board
        <select value={values.board} onChange={(event) => onChange('board', event.target.value)}>
          <option value="CBSE">CBSE</option>
          <option value="ICSE">ICSE</option>
          <option value="KA_STATE">Karnataka</option>
        </select>
      </label>

      <label>
        Grade
        <select value={values.grade} onChange={(event) => onChange('grade', event.target.value)}>
          {Array.from({ length: 12 }, (_, i) => i + 1).map((grade) => (
            <option key={grade} value={grade}>
              {grade}
            </option>
          ))}
        </select>
      </label>

      <label>
        Subject
        <select value={values.subject} onChange={(event) => onChange('subject', event.target.value)}>
          {subjects.map((subject) => (
            <option key={subject} value={subject}>
              {subject}
            </option>
          ))}
        </select>
      </label>

      <label>
        Start Date
        <input
          type="date"
          value={values.start_date}
          onChange={(event) => onChange('start_date', event.target.value)}
          required
        />
      </label>

      <label>
        End Date
        <input
          type="date"
          value={values.end_date}
          onChange={(event) => onChange('end_date', event.target.value)}
          required
        />
      </label>

      <label>
        Special Instructions
        <textarea
          value={values.instructions}
          onChange={(event) => onChange('instructions', event.target.value)}
          rows={4}
          placeholder="Optional"
        />
      </label>

      <button type="submit" disabled={submitting}>
        Generate Plan
      </button>
    </form>
  );
};

export default PlannerForm;
