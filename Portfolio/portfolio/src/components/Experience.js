// Experience.js
import React from 'react';
import './Experience.css';

const Experience = ({ experiences }) => {
  return (
    <div className="experience">
      <h3>Experience</h3>
      <div className="experience-list">
        {experiences.map(exp => (
          <div key={exp.id} className="experience-item">
            <h4>{exp.title}</h4>
            <p>{exp.duration}</p>
            <p>{exp.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Experience;
