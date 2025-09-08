import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import cors from "cors";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(express.static(path.join(__dirname, "public")));

// Endpoint for simulated messaging
app.post("/send-message", (req, res) => {
  const { message, token, convoId } = req.body;
  console.log(`[SIMULATION] Message sent: "${message}" to convoId: ${convoId} using token: ${token}`);
  // Simulate success response
  res.json({ success: true, message: "Message simulated successfully." });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
