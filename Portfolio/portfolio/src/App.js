// App.js
import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import Profile from './components/Profile';
import Projects from './components/Projects';
import Experience from './components/Experience';
import Education from './components/Education';
import ProjectDetail from './components/ProjectDetails'; // Ensure the component name matches your file
import projectsData from './utils/loadProjects'; // Import the projects data
import './App.css';

const App = () => {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Load projects from imported data
    const loadedProjects = Object.values(projectsData);
    setProjects(loadedProjects);
  }, []);

  useEffect(() => {
    const pathParts = location.pathname.split('/');
    if (pathParts[1] === 'projects' && pathParts[2]) {
      setSelectedProjectId(parseInt(pathParts[2], 10));
    } else {
      setSelectedProjectId(null);
    }
  }, [location]);

  const handleProjectSelect = (projectId) => {
    navigate(`/projects/${projectId}`);
  };

  const handleBack = () => {
    navigate('/projects');
  };

  // Define user, experiences, and education
  const user = {
    name: 'Smitkumar Patel',
    title: 'Data Analyst at Amazon',
    location: 'London, UK',
    image: 'path_to_image',
    links: [
      { name: 'LinkedIn', url: 'https://www.linkedin.com' },
      { name: 'Kaggle', url: 'https://www.kaggle.com' }
    ],
    email: 'alexander.marks@example.com',
    about: 'Quantitative economics graduate...',
    skills: ['SQL', 'Python', 'R', 'Tableau', 'Excel', 'Statistical modelling', 'Sampling techniques']
  };

  const experiences = [
    {
      id: 1,
      title: 'Experience One',
      description: 'Description of experience one',
      duration: 'Jan 2020 - Present'
    },
    // Add more experiences as needed
  ];

  const education = [
    {
      id: 1,
      title: 'Education One',
      description: 'Description of education one',
      duration: '2016 - 2020'
    },
    // Add more education items as needed
  ];

  const selectedProject = projects.find(p => p.id === selectedProjectId);

  return (
    <div className="container">
      <div className="app">
        <Routes>
          <Route path="/projects" element={
            <Projects projects={projects} onProjectSelect={handleProjectSelect} />
          } />
          <Route path="/projects/:id" element={
            <ProjectDetail project={selectedProject} onBack={handleBack} />
          } />
          {/* Add other routes here */}
        </Routes>
      </div>

      <div className="left-column">
        <Profile user={user} />
      </div>
      <div className="right-column">
        {selectedProject ? (
          <ProjectDetail project={selectedProject} onBack={handleBack} />
        ) : (
          <>
            <div className="section">
              <Projects projects={projects} onProjectSelect={handleProjectSelect} />
            </div>
            <div className="section">
              <Experience experiences={experiences} />
            </div>
            <div className="section">
              <Education education={education} />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default App;
