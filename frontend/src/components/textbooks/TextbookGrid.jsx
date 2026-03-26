import React from 'react';
import TextbookCard from './TextbookCard';
import './TextbookGrid.css';

const TextbookGrid = ({ textbooks }) => {
  return (
    <div className="textbook-grid">
      {textbooks.map((textbook) => (
        <TextbookCard key={textbook.id} textbook={textbook} />
      ))}
    </div>
  );
};

export default TextbookGrid;
