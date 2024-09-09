const axios = require('axios');
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

app.get('/exchange-code', async (req, res) => {
  const code = req.query.code;
  if (!code) {
    return res.status(400).send('Authorization code is required');
  }

  const clientId = 'KGCD5ryo5PMEPI0I5jI5KkGgon2qtizfkumuN5wm';
  const clientSecret = 'PndtJOg7t5vRkyQhTfHqbhnCv5SZ9r1V3vZNjsAyLs0rhRwcObcZQMQX4xlZPlbA0qBRfX0tuYby2koSLR5t2CIyjVpuEwbyBCActJy61nEQZBmxcCLxJwo6q6Vx8hfA';
  const redirectUri = 'https://cuddly-acorn-5gg655g9gr4vfqqq-3000.app.github.dev/oauth-callback';

  try {
    const response = await axios.post('https://drchrono.com/o/token/', new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri,
      code: code,
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const accessToken = response.data.access_token;
    console.log('Access Token:', accessToken);

    res.json({ accessToken });
  } catch (error) {
    console.error('Error exchanging code for token:', error.response ? error.response.data : error.message);
    res.status(500).send('Error exchanging code for token');
  }
});

const PORT = 4000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
