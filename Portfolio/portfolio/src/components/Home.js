import React from 'react';
import Profile from './Profile';
import Projects from './Projects';
import Experience from './Experience';
import Education from './Education';

const profileData = {
  name: 'Alexander Marks',
  title: 'Data Analyst at Amazon',
  location: 'London, UK',
  about: 'Quantitative economics graduate, enjoy working with business stakeholders to help support strategy based on quantitative insights and statistical models.',
  skills: ['SQL', 'Python', 'R', 'Tableau', 'Excel', 'Statistical modelling', 'Sampling techniques'],
  image: 'path_to_profile_image'
};

const projects = [
  {
    id: 1,
    title: 'AirBnB listings price prediction',
    description: 'Prediction of AirBnB prices growth Milan (Italy) to provide insights on the areas that might soon get more opportunities to monetize with short stays. The algorithm takes into account seasonality, home characteristics, economic factors and stats on existing properties.',
    image: 'path_to_project_image_1',
    skills: ['Python', 'SQL', 'Matlab'],
    link: '/project/1'
  },
  {
    id: 2,
    title: 'Spotify visual data art',
    description: 'Inspired by Windows Music Player animations, this algorithm creates cool animations for every music track on earth. The animations are tailored to the melody as well as the text, with the aim to create engaging experiences for users.',
    image: 'path_to_project_image_2',
    skills: ['Python', 'Javascript', 'SQL'],
    link: '/project/2'
  }
];

const experience = {
  title: 'Data Analyst at Amazon',
  date: 'Mar 2022 - now',
  description: 'Leading the development and implementation of data analytics strategies that support business goals. Managing a team of data analysts to ensure data accuracy, completeness, and integrity. Providing insights and recommendations to senior management based on analysis of customer behaviour, product performance, and other key metrics.',
  skills: ['SQL', 'Python', 'R', 'Excel', 'Tableau']
};

const education = {
  date: '2022',
  degree: 'Quantitative Economics, Master of Science, University of London',
  description: 'High quality quantitative training in economics, a focus on advanced research methods and a supervised research thesis. Rigorous grounding in using mathematical and statistical methods to derive, test and apply formal economic models'
};

const Home = () => {
  return (
    <div className="container">
      <div className="left-column">
        <Profile profile={profileData} />
      </div>
      <div className="right-column">
        <Projects projects={projects} />
        <Experience experience={experience} />
        <Education education={education} />
      </div>
    </div>
  );
};

export default Home;
