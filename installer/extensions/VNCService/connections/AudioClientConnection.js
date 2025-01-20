const net = require('net')

class AudioClientConnection {

    constructor(ws) {
        this.tcpClient = new net.Socket();
        this.isConnected = false;
        this.ws = ws;

        this.ws.on('message', (m) => {
            this.handle(m)
        });

        this.ws.on('close', () => {
            console.log('Connection closed')
            this.disconnect();
        });

        this.ws.on('error', (err) => {
            console.error('WebSocket Error:', err.message);
            this.isConnected = false;
            this.ws.send('WebSocket Error: ' + err.message);
        });

        this.tcpClient.on('error', (e) => {
            console.log('could not reach vm')
            this.ws.send('Error: Could not reach VM or Container')
        })
    }

    // If not connected to remote vm, try to connect. Else forward audio.
    handle(message){
        try{
            if(this.isConnected){
                this.tcpClient.write(message)
            }else{
                this.connect(message);
            }
        } catch (e){

        }
    }

    connect(destination){
        try{
            this.tcpClient.connect(8080, destination, () => {
                this.isConnected = true;
                console.log('Client connected to VM Audio Server.')
                this.ws.send('Connected')
            })
        } catch(e){
            console.log(e)
        }
    }

    disconnect(){
        this.tcpClient.end();
        //this.tcpClient.destroy();
    }

}

module.exports = AudioClientConnection;