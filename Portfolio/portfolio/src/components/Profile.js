// Profile.js
import React from 'react';
import './Profile.css';

const Profile = ({ user }) => {
  return (
    <div className="profile">
      <img src={user.image} alt={user.name} className="profile-image" />
      <h1>{user.name}</h1>
      <h2>{user.title}</h2>
      <p>{user.location}</p>
      <div className="profile-links">
        {user.links.map(link => (
          <a key={link.name} href={link.url} target="_blank" rel="noopener noreferrer">{link.name}</a>
        ))}
      </div>
      <button>Email me</button>
      <div className="profile-about">
        <h3>About</h3>
        <p>{user.about}</p>
      </div>
      <div className="profile-skills">
        <h3>Skills</h3>
        <div>
          {user.skills.map(skill => (
            <span key={skill} className="profile-skill">{skill}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Profile;
