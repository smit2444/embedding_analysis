import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import projectsData from '../utils/loadProjects'; // Import the projects data directly

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // Find the project by ID
  const project = projectsData[id];

  if (!project) {
    return <div>Project not found</div>;
  }

  return (
    <div className="project-detail">
      <button onClick={() => navigate('/projects')}>&larr; back</button>
      <h1>{project.title}</h1>
      <img src={project.image} alt={project.title} className="project-detail-image" />
      <div className="project-detail-skills">
        {project.skills.map(skill => <span key={skill} className="project-detail-skill">{skill}</span>)}
      </div>
      <div className="project-detail-description" dangerouslySetInnerHTML={{ __html: project.description }} />
    </div>
  );
};

export default ProjectDetail;
