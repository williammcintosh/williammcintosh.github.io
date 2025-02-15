exports.handler = async function () {
  return {
    statusCode: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ apiKey: process.env.GOOGLE_API_KEY }),
  };
};
