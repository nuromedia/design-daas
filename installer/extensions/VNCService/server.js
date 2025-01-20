const express = require("express");
const enableWs = require("express-ws");
const { exec } = require("child_process");
const fs = require("fs");
const { type } = require("os");

const app = express();
enableWs(app);
app.use(express.json());

var sessions = new Map();

app.ws("/vnc/printer", async (ws, req) => {
  const userID = req.query.id;
  console.log(`New print client connection: id=${userID}`);
  sessions.set(userID, ws);

  try {
    const result = await createPrinter(userID);
    ws.send(JSON.stringify({ type: "status", status: result }));
    ws.send(
      JSON.stringify({
        type: "printer_path",
        printer_path: `/printers/${userID}`,
      }),
    );
  } catch (error) {
    ws.send(JSON.stringify({ status: error }));
  }
  ws.on("close", () => {
    sessions.delete(userID);
  });
});

// For notifications that pdf is created
app.post("/api/vnc/file", (req, res) => {
  const data = req.body;
  console.log("New file: " + data["message"]);
  handlePath(data["message"]);
  res.json({ status: "Path processed" });
});

// Help functions

function handlePath(path) {
  const clientId = path.split("/")[5]; // Extract the client id from the path
  const ws = sessions.get(clientId);
  const relativePath = `files/${clientId}/${path.split("/")[2]}`; // Extract the relative part of the file path

  if (ws) sendFile(path, ws);
  else console.log(`No active session for client ${clientId}`);
}

function generateRandomString(length) {
  const characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  const charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}

function sendFile(path, ws) {
  console.log("Sending file: " + path);
  const stream = fs.createReadStream(path);
  const name = path.split("/").pop();
  const mimetype = "application/pdf";
  const randid = generateRandomString(16);
  ws.send(JSON.stringify({ type: "file-begin", name, randid, mimetype }));

  stream.on("data", (data) => {
    const data64 = data.toString("base64");
    ws.send(
      JSON.stringify({
        type: "file-chunk",
        name,
        randid,
        mimetype,
        data: data64,
      }),
    );
  });

  stream.on("end", () => {
    ws.send(
      JSON.stringify({ type: "file-end", name, randid, mimetype, mimetype }),
    );
    fs.unlink(path, (err) => {
      if (err) throw err;
      console.log(`File ${path} was deleted`);
    });
  });
}

async function createPrinter(name) {
  console.log("Creating printer: " + name);
  const path = `/usr/src/app/scripts/create_printer.sh ${name}`;

  return new Promise((resolve, reject) => {
    exec(path, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error creating printer: ${stderr}`);
        reject("error: could not create printer");
      } else {
        console.log(`Printer ${name} is running: ${stdout}`);
        resolve("printer is ready");
      }
    });
  });
}

app.listen(8010);

console.log("Server is running...");

