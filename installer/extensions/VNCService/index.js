const express = require('express');
const http = require('http');
const cors = require('cors')
const PrintServer = require('./servers/PrintServer');
const AudioServer = require('./servers/AudioServer');


const app = express();
app.use(cors())
app.use(express.json())
app.use('/files', express.static('/usr/src/app/files')) // File server

// Printer server
const printHttpServer = http.createServer(app)
const printServer = new PrintServer(printHttpServer, app)

printHttpServer.listen(8010, () => {
    console.log('Print server is listening on port 8010')
})

// Microphone Server
const audioHttpServer = http.createServer(app);
const audioServer = new AudioServer(audioHttpServer);
audioHttpServer.listen(8020, () => {
    console.log('Audio Server is up.')
})


