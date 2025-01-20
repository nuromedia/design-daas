const WebSocket = require('ws');
const PrintClient = require('../clients/PrintClient');
const express = require('express')

class PrintServer{

    static id = 1;  // Session ID counter

    constructor(server, app){
        this.server = server;
        this.wss = null;
        this.sessions = new Map();
        this.router = express.Router();
        this.service = new PrintClient('http://192.168.178.29:5000');
        this.setupRoutes(app);
    }

    // Initialize the server (Subscribe for notifications)
    async init(){
        const response = await this.service.subscribe('http://192.168.178.29:8010/print/file')
        console.log("Response:" + response)
        if(response.status == 200){
            this.wss = new WebSocket.Server({server: this.server});
            this.wss.on('connection', this.onConnection.bind(this));
            console.log('Server connected to Printing component and running.')
        }else{
            console.log('Could not connect to Printer Component.')
        }
    }

    // Rest API for receiving notifications when a file is printed
    setupRoutes(app){
        this.router.post('/file', (req, res) => {
            const data = req.body;
            console.log(data)

            this.sendFile(data['message'])
            res.json({ status: 'Path processed'});
        });
        app.use('/print', this.router)
    }

    // Handle new connections
    async onConnection(ws){
        const id = 'client_' + PrintServer.id;
        PrintServer.id++;
        console.log(`New connection with id: ${id}`);
        this.sessions.set(id, ws);

        await this.service.createPrinter(id);

        const printer_path = `http://192.168.178.29/printers/${id}`

        ws.send(JSON.stringify({printer_path}))

        ws.on('close', () => {
            console.log(`Connection with id: ${id} closed.`)
            this.service.deletePrinter(id);
        })
        
    }
    
    // Send file path to client
    sendFile(path){
        console.log(`Sending file ${path}`)
        const clientId = path.split('/')[1];
        console.log('Extracted client id: ' + clientId);
        console.log(path.split('/'))
        const ws = this.sessions.get(clientId);
        const absPath = `http://localhost:8010/files/${clientId}/${path.split('/')[2]}`

        if (ws) {
            ws.send(JSON.stringify({path : absPath}));
            console.log(`File path sent to client ${clientId}`);
        } else {
            console.log(`No active session for client ${clientId}`);
        }
    }

}

module.exports = PrintServer