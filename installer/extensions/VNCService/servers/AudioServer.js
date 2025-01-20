const WebSocket = require('ws');
const AudioClientConnection = require('../connections/AudioClientConnection')


class AudioServer{

    static id = 1;
 
    constructor(server){
        this.wss = new WebSocket.Server({server})
        this.wss.on('connection', this.onConnection.bind(this));
        this.sessions = new Map();
    }

    // Handle incomming connections
    async onConnection(ws){
        console.log('New audio connection with id: ' + AudioServer.id);
        const client_id = AudioServer.id;
        AudioServer.id++;
        this.sessions.set(client_id, ws);

        const connection = new AudioClientConnection(ws);
    }

}

module.exports = AudioServer