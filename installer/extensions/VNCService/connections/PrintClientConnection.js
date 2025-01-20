const {exec} = require('child_process');
const { json } = require('express');
const { stdout } = require('process');
 
class PrintClientConnection {

    constructor(ws, server) {

        this.ws = ws;
        this.server = server;

        // For now the client sends its id, which is used as session identifyier and printer identifyier
        this.ws.on('message', (m) => {
            console.log(`Print client ${m} connected`)
            server.addConnection(m, ws)
            this.createPrinter(m)
        });
    }

    createPrinter(name) {
        console.log('Creating printer: ' + name);
        const path = `/usr/src/app/scripts/create_printer.sh ${name}`

        exec(path, (error, stdout, stderr) => {
            if(error){
                console.log('Error: ' + error)
            }
            else {
                // If printer is created or is already existing, send its relative path
                console.log(`Printer ${name} is running`);
                const printer_path = `printers/${name}`;
                this.ws.send(JSON.stringify({printer_path}))
            }
           console.log('create_printer script executed')

        });
    }
}

module.exports = PrintClientConnection;