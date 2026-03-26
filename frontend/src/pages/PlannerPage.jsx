import React, { useState } from 'react';
import PlannerForm from '../components/planner/PlannerForm';
import GeneratingLoader from '../components/planner/GeneratingLoader';
import PlanResult from '../components/planner/PlanResult';
import { generatePlan } from '../api/planner';
import './PlannerPage.css';

const PlannerPage = () => {
  const [values, setValues] = useState({
    teacher_name: '',
    board: 'CBSE',
    grade: 5,
    subject: 'Maths',
    start_date: '',
    end_date: '',
    instructions: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (field, value) => {
    setValues((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const payload = {
        teacher_name: values.teacher_name,
        board: values.board,
        grade: Number(values.grade),
        subject: values.subject,
        start_date: values.start_date,
        end_date: values.end_date,
        instructions: values.instructions,
      };
      const data = await generatePlan(payload);
      setResult(data);
    } catch (err) {
      const message = err?.response?.data?.error || 'Failed to generate plan. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="planner-page">
      <header>
        <h1>AI Course Completion Planner</h1>
        <p>Generate a week-by-week plan with Claude and get a PDF instantly.</p>
      </header>

      {submitting && <GeneratingLoader />}

      {!submitting && error && <div className="error-box">{error}</div>}

      {!submitting && !result && (
        <PlannerForm
          values={values}
          onChange={handleChange}
          onSubmit={handleSubmit}
          submitting={submitting}
        />
      )}

      {!submitting && result && <PlanResult result={result} />}
    </section>
  );
};

export default PlannerPage;
