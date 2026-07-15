import { connectDB } from "./db.js";
import { PORT } from "./config.js";
import app from "./app.js";
import { Server } from "socket.io";
import http from "http";
import router from "./routes/posts_routes.js";
import HeatingStatus from "./models/HeatingStatus.js";
import HeatingTemp from "./models/HeatingTemp.js";

connectDB();

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST", "PUT"],
  },
});

router.put("/update-status/:id", async (req, res) => {
  try {
    const updateStatus = await HeatingStatus.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );

    console.log("updateStatus", updateStatus);

    io.emit("socket_status", updateStatus);

    if (updateStatus.status === 1) {
      return res.json({ message: "On" });
    } else {
      return res.json({ message: "Off" });
    }
  } catch (error) {
    console.log(error);
  }
});

router.post("/sendSenzorTemperatureAndHumidity", (req, res) => {
  const data = req.body;

  io.emit("socket_temperature_And_Humidity", {
    humidity: data.humidity,
    temperature: data.temperature,
  });

  const response = {
    message: "Datele de la senzori au fost primite cu succes!",
    body: data,
  };

  res.json(response);
});

router.put("/update-treshold/:id", async (req, res) => {
  try {
    const updateTreshold = await HeatingTemp.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );

    io.emit("socket_treshold", updateTreshold.temperature);

    return res.json({ message: "ok" });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
});

router.put("/update-treshold-from-web/:id", async (req, res) => {
  try {
    const updateTreshold = await HeatingTemp.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );

    if (updateTreshold) {
      return res.json({ message: "ok" });
    }
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
});

io.on("connection", (socket) => {
  console.log("a user connected" + socket.id);
});

server.listen(PORT);
console.log(`Server is running port ${PORT}`);
