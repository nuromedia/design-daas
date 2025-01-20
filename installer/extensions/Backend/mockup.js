const express = require('express')
const enableWs = require('express-ws')
const WebSocket = require('ws')
const net = require('net');
const config = require('./config')

const app = express()
enableWs(app)
app.use(express.json())

var print_clients = new Map();

// Printer API
app.ws('/vnc/printer', (ws, req) => {
    const token = req.query.token;
    const userID = req.query.id;
    console.log(`New print client connection: token=${token}, id=${userID}`)

    print_clients.set(userID, ws)

    // Validate token

    const proxy = new WebSocket(`${config.vncPrinerAPI}?id=${userID}`);
    
    ws.onmessage = (m) => {
        proxy.send(m.data)  // Forward to printer container
    }

    proxy.onmessage = (m) => {
        ws.send(m.data) // Forward to web-client
    }

    ws.on('close', () => {
        print_clients.delete(userID)
        proxy.close();
    })
})

// Microphone API
app.ws('/vnc/audio', (ws, req) => {
    const token = req.query.token;
    const destination = req.query.destination;

    // Validate token

    console.log(`New audio client connection: token=${token}, destination=${destination}`)

    const audioClient = new net.Socket();
    audioClient.connect(config.microphonePort, destination, () => {
        ws.send('connected');
    });

    audioClient.on('error', (e) => {
        ws.send("Error")
    });

    audioClient.on('close', () => {
        ws.send('connection to VM closed')
    })

    ws.on('message', data => {
        audioClient.write(data)
    })

    ws.on('close', () => {
        audioClient.end();
    })
})

// ToDo CUPS Proxy API

app.listen(8000)