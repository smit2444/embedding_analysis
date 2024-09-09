import React, { useEffect } from 'react';
import axios from 'axios';

const ProcessCode = ({ code }) => {
  useEffect(() => {
    const exchangeCode = async () => {
      try {
        const response = await axios.post('https://cuddly-acorn-5gg655g9gr4vfqqq-4000.app.github.dev/exchange-code', { code });
        console.log('Access Token:', response.data.accessToken);
        console.log('Refresh Token:', response.data.refreshToken);
        console.log('Expires At:', new Date(response.data.expiresAt));
      } catch (error) {
        console.error('Error exchanging code:', error);
      }
    };

    if (code) {
      exchangeCode();
    }
  }, [code]);

  return <div>Processing Authorization...</div>;
};

export default ProcessCode;
