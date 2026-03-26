import React, { useEffect, useState } from 'react';
import BoardSelector from '../components/textbooks/BoardSelector';
import GradeFilter from '../components/textbooks/GradeFilter';
import SubjectFilter from '../components/textbooks/SubjectFilter';
import TextbookGrid from '../components/textbooks/TextbookGrid';
import { fetchTextbooks } from '../api/textbooks';
import './TextbooksPage.css';

const SUBJECTS = ['Maths', 'Science', 'English', 'Social Studies', 'Hindi', 'Kannada'];

const TextbooksPage = () => {
  const [board, setBoard] = useState('CBSE');
  const [grade, setGrade] = useState('');
  const [subject, setSubject] = useState('');
  const [textbooks, setTextbooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const params = {
          board,
          ...(grade ? { grade } : {}),
          ...(subject ? { subject } : {}),
        };
        const data = await fetchTextbooks(params);
        setTextbooks(data);
      } catch (err) {
        setError('Failed to load textbooks. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [board, grade, subject]);

  return (
    <section className="textbooks-page">
      <header>
        <h1>Textbook Library</h1>
        <p>Browse official textbooks by board, grade, and subject.</p>
      </header>

      <BoardSelector value={board} onChange={setBoard} />

      <div className="filters">
        <GradeFilter value={grade} onChange={setGrade} />
        <SubjectFilter value={subject} onChange={setSubject} subjects={SUBJECTS} />
      </div>

      {loading && (
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="skeleton-card" />
          ))}
        </div>
      )}

      {!loading && error && <div className="error-box">{error}</div>}

      {!loading && !error && textbooks.length === 0 && (
        <div className="empty-state">No textbooks found for these filters.</div>
      )}

      {!loading && !error && textbooks.length > 0 && (
        <TextbookGrid textbooks={textbooks} />
      )}
    </section>
  );
};

export default TextbooksPage;
