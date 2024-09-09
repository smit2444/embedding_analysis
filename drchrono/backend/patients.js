// const axios = require('axios');
// const { Parser } = require('json2csv');
// const fs = require('fs');

// const accessToken = 'dMQgdwE5D0TU3QMIEygSlfdG2wkNel'; // Ensure this token has the required scopes

// const fetchTransactions = async (params = {}) => {
//   try {
//     // Construct the URL with query parameters
//     const baseUrl = 'https://app.drchrono.com/api/transactions/';
//     const response = await axios.get(baseUrl, {
//       headers: {
//         Authorization: `Bearer ${accessToken}`,
//         'Content-Type': 'application/json',
//       },
//       params: params, // Include the query parameters
//     });

//     if (response.status >= 200 && response.status < 300) {
//       console.log('Successful response:', response.data);

//       // Convert JSON response to CSV
//       const json2csvParser = new Parser();
//       const csv = json2csvParser.parse(response.data.results);

//       // Write the CSV data to a file
//       fs.writeFile('transactions.csv', csv, (err) => {
//         if (err) {
//           console.error('Error writing CSV to file:', err);
//         } else {
//           console.log('CSV file successfully written as transactions.csv');
//         }
//       });
//     } else if (response.status >= 300 && response.status < 400) {
//       console.log('Redirection response:', response.status);
//       // Handle redirection if needed (e.g., follow the redirect)
//     } else {
//       console.log('Unexpected response status:', response.status);
//     }
//   } catch (error) {
//     console.error('Error fetching transactions:', error.response ? error.response.data : error.message);
//   }
// };

// // Example parameters - customize as needed
// const params = {
//   // since: '2014-08-01T00:00:00', // Example date
//   posted_date: '2015-08-01T00:00:00', // Example posted date
//   // line_item: 123, // Example line item ID (if needed)
//   // page_size: 50, // Number of results per page
//   // cursor: 'next_cursor', // Example cursor for pagination (if applicable)
// };

// // Call the function to fetch transactions with parameters
// fetchTransactions(params);


const axios = require('axios');
const { Parser } = require('json2csv');
const fs = require('fs');

const accessToken = '7MDYnPyQddpEV6nB08WwJdoX3gOYLa';

const fetchPatients = async () => {
  try {

    const response = await axios.get('https://app.drchrono.com/api/transactions_list', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        // 'Content-Type': 'application/json',
      },
    });

    console.log(response.data);
    const json2csvParser = new Parser();
    const csv = json2csvParser.parse(response.data.results);

    fs.writeFile('patients.csv', csv, (err) => {
      if (err) {
        console.error('Error writing CSV to file:', err);
      } else {
        console.log('CSV file successfully written as patients.csv');
      }
    });
  } catch (error) {
    console.error('Error fetching patients:', error.response ? error.response.data : error.message);
  }
};

fetchPatients();
