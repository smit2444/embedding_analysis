// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AuthorizationButton from './components/AuthorizationButton';
import OAuthCallbackHandler from './components/OAuthCallbackHandler';
import Dashboard from './components/Dashboard';

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<AuthorizationButton />} />
      <Route path="/oauth-callback" element={<OAuthCallbackHandler />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  </Router>
);

export default App;
