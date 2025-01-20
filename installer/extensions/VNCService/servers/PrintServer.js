const WebSocket = require('ws');
const PrintClientConnection = require('../connections/PrintClientConnection');
const express = require('express')

class PrintServer {

    constructor(server, app) {
        this.sessions = new Map();
        this.wss = new WebSocket.Server({server});
        this.wss.on('connection', this.onConnection.bind(this));
        this.router = express.Router();
        this.setupRoutes(app);
    }

    addConnection(id, ws){
        this.sessions.set(id, ws)
    }

    async onConnection(ws) {
        console.log('New printer connection')
        const connection = new PrintClientConnection(ws, this)
    }

    setupRoutes(app){
        // Receives the path of the created PDF file
        this.router.post('/file', (req, res) => {
            const data = req.body;
            console.log('New file: ' + data['message'])
            this.handlePath(data['message'])
            res.json({ status: 'Path processed'});
        });
        app.use('/print', this.router)
    }

    handlePath(path){
        const clientId = path.split('/')[1];    // Extract the client id from the path
        const ws = this.sessions.get(clientId);
        const relativePath = `files/${clientId}/${path.split('/')[2]}`  // Extract the relative part of the file path

        if(ws)
            ws.send(JSON.stringify({file_path: relativePath}))
        else
            console.log(`No active session for client ${clientId}`);
    }
    
}

module.exports = PrintServer