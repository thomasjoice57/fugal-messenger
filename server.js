import express from 'express';
import fetch from 'node-fetch';
import cors from 'cors';
import multer from 'multer';

const app = express();
const upload = multer();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

app.post('/send-message', upload.none(), async (req, res) => {
    const { access_token, message, convo_id } = req.body;
    if (!access_token || !message || !convo_id) {
        return res.status(400).json({ error: 'Missing fields' });
    }

    try {
        const url = `https://graph.facebook.com/v17.0/${convo_id}/messages`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token, message })
        });
        const data = await response.json();
        if (response.ok) {
            return res.json({ success: true, data });
        } else {
            return res.status(400).json({ success: false, data });
        }
    } catch (err) {
        return res.status(500).json({ success: false, error: err.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
