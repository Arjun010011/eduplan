import React from 'react';
import { NavLink, Routes, Route, Navigate } from 'react-router-dom';
import TextbooksPage from './pages/TextbooksPage';
import PlannerPage from './pages/PlannerPage';
import './App.css';

const App = () => {
  return (
    <div className="app-shell">
      <nav className="app-nav">
        <div className="brand">EduPlan</div>
        <div className="nav-links">
          <NavLink to="/textbooks" className={({ isActive }) => (isActive ? 'active' : '')}>
            📚 Textbooks
          </NavLink>
          <NavLink to="/planner" className={({ isActive }) => (isActive ? 'active' : '')}>
            📅 Course Planner
          </NavLink>
        </div>
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/textbooks" replace />} />
          <Route path="/textbooks" element={<TextbooksPage />} />
          <Route path="/planner" element={<PlannerPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
