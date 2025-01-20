
const net = require('net');

class AudioClient{

    constructor(ws){
        this.client = new net.Socket();
        this.isConnected = false;
        this.ws = ws;

        this.client.on('close', () => {
            console.log('Connection closed')
        });

        this.client.on('error', (err) => {
            console.error('Socket error:', err.message);
            this.isConnected = false;
            this.ws.send('Connection Error: ' + err.message);
        });

    }

    handle(message){
        try{
            if(this.isConnected){
                this.client.write(message)
            }else{
                this.connect(message);
            }
        } catch (e){

        }
    }

    connect(destination){
        try{
            this.client.connect(8080, destination, () => {
                this.isConnected = true;
                console.log('Client connected to VM Audio Server.')
                this.ws.send('Connected')
            })
        } catch(e){
            console.log(e)
        }
    }

    disconnect(){
        this.client.end();
        this.client.destroy();
    }

}

module.exports = AudioClient;