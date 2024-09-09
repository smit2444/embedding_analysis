import axios from 'axios';

const getAccessToken = async () => {
  const clientId = 'KGCD5ryo5PMEPI0I5jI5KkGgon2qtizfkumuN5wm';
  const clientSecret = 'PndtJOg7t5vRkyQhTfHqbhnCv5SZ9r1V3vZNjsAyLs0rhRwcObcZQMQX4xlZPlbA0qBRfX0tuYby2koSLR5t2CIyjVpuEwbyBCActJy61nEQZBmxcCLxJwo6q6Vx8hfA';
  const tokenUrl = 'https://drchrono.com/o/token/';

  const params = new URLSearchParams();
  params.append('grant_type', 'client_credentials');
  params.append('client_id', clientId);
  params.append('client_secret', clientSecret);

  try {
    const response = await axios.post(tokenUrl, params);
    return response.data.access_token;
  } catch (error) {
    console.error('Error fetching access token:', error);
    return null;
  }
};
const fetchUserData = async (accessToken) => {
    const apiUrl = 'https://app.drchrono.com/api/users';
  
    try {
      const response = await axios.get(apiUrl, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user data:', error);
      return null;
    }
  };
  
  // Example usage in a React component
  import React, { useEffect, useState } from 'react';
  
  const App = () => {
    const [userData, setUserData] = useState(null);
  
    useEffect(() => {
      const fetchData = async () => {
        const token = await getAccessToken();
        if (token) {
          const data = await fetchUserData(token);
          setUserData(data);
        }
      };
  
      fetchData();
    }, []);
  
    return (
      <div>
        <h1>User Data</h1>
        {userData ? (
          <pre>{JSON.stringify(userData, null, 2)}</pre>
        ) : (
          <p>Loading...</p>
        )}
      </div>
    );
  };
  
  export default App;
  