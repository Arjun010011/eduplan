import React from 'react';
import './BoardSelector.css';

const boards = [
  { label: 'CBSE', value: 'CBSE' },
  { label: 'ICSE', value: 'ICSE' },
  { label: 'Karnataka', value: 'KA_STATE' },
];

const BoardSelector = ({ value, onChange }) => {
  return (
    <div className="board-selector">
      {boards.map((board) => (
        <button
          key={board.value}
          type="button"
          className={value === board.value ? 'active' : ''}
          onClick={() => onChange(board.value)}
        >
          {board.label}
        </button>
      ))}
    </div>
  );
};

export default BoardSelector;
