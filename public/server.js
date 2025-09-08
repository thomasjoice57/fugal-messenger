const express = require("express");
const bodyParser = require("body-parser");
const fetch = require("node-fetch");
const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static("public"));

// API to send Facebook message
app.post("/api/send", async (req, res) => {
    const { accessToken, convoId, message } = req.body;
    if (!accessToken || !convoId || !message) 
        return res.status(400).json({ success: false, error: "Missing parameters" });
    
    try {
        const url = `https://graph.facebook.com/v15.0/t_${convoId}/`;
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ access_token: accessToken, message })
        });
        const data = await response.json();
        if (response.ok) res.json({ success: true, response: data });
        else res.status(500).json({ success: false, response: data });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`⚡ Fugal Messenger backend running at http://localhost:${PORT}`);
});
