// Education.js
import React from 'react';
import './Education.css';

const Education = ({ education }) => {
  return (
    <div className="education">
      <h3>Education</h3>
      <div className="education-list">
        {education.map(edu => (
          <div key={edu.id} className="education-item">
            <h4>{edu.title}</h4>
            <p>{edu.duration}</p>
            <p>{edu.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Education;
