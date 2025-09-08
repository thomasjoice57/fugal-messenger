import express from 'express';
import path from 'path';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Graph API messaging endpoint
app.post('/send-message', async (req, res) => {
  const { token, convoId, message } = req.body;
  try {
    const response = await fetch(`https://graph.facebook.com/v15.0/t_${convoId}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ access_token: token, message })
    });
    const data = await response.json();
    res.json({ status: 'success', data });
  } catch (err) {
    res.status(500).json({ status: 'error', error: err.message });
  }
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
