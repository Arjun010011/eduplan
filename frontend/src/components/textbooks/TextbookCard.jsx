import React from 'react';
import './TextbookCard.css';

const TextbookCard = ({ textbook }) => {
  return (
    <div className="textbook-card">
      <div className="cover">
        {textbook.cover_image_url ? (
          <img src={textbook.cover_image_url} alt={textbook.title} />
        ) : (
          <div className="placeholder">No Cover</div>
        )}
      </div>
      <div className="card-content">
        <div className="grade-badge">Grade {textbook.grade}</div>
        <h3>{textbook.title}</h3>
        <p className="subject">{textbook.subject}</p>
        <a className="download" href={textbook.file_url} target="_blank" rel="noreferrer">
          Download PDF
        </a>
      </div>
    </div>
  );
};

export default TextbookCard;
