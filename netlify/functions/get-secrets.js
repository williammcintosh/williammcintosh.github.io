const fetch = require('node-fetch');

exports.handler = async function () {
  const apiKey = process.env.GOOGLE_DRIVE_API_KEY; // Securely stored in Netlify env vars
  const folderId = '1x2iC7QAf8vH2rRu4jg_OU-KOACls8zNz';
  const url = `https://www.googleapis.com/drive/v3/files?q='${folderId}'+in+parents&key=${apiKey}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    return {
      statusCode: 200,
      body: JSON.stringify(data),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to fetch Google Drive files.' }),
    };
  }
};
