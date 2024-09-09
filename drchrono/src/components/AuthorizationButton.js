import React from 'react';

const clientId = 'KGCD5ryo5PMEPI0I5jI5KkGgon2qtizfkumuN5wm';
const redirectUri = 'https://cuddly-acorn-5gg655g9gr4vfqqq-3000.app.github.dev/oauth-callback';
const scope = 'patients:read patients:write billing:read billing:write billing:patient-payment:read'; // Adjust the scope based on your needs

const authorizationUrl = `https://drchrono.com/o/authorize/?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}`;

const AuthorizationButton = () => {
  const handleAuthorization = () => {
    window.location.href = authorizationUrl;
  };

  return (
    <button onClick={handleAuthorization}>
      Authorize with DrChrono
    </button>
  );
};

export default AuthorizationButton;


