// src/utils/loadProjects.js
function importAll(r) {
    let projects = {};
    r.keys().forEach((item) => { 
      const project = r(item);
      projects[project.id] = project;
    });
    return projects;
  }
  
  const projects = importAll(require.context('../data/projects', false, /\.json$/));
  
  export default projects;
  