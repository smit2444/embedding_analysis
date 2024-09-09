import React from 'react';
import projectsData from '../utils/loadProjects'; // Import the projects data directly

const Projects = ({ onProjectSelect }) => {
  // Convert the projectsData object to an array
  const projects = Object.values(projectsData);

  return (
    <div className="projects">
      {projects.map(project => (
        <div key={project.id} className="project">
          <h2>{project.title}</h2>
          <p>{project.description}</p>
          <button onClick={() => onProjectSelect(project.id)}>Read more</button>
        </div>
      ))}
    </div>
  );
};

export default Projects;
