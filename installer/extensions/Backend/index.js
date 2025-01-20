const GuacamoleLite = require('guacamole-lite');
const express = require('express');
const http = require('http');
const PrintServer = require('./servers/PrintServer2');
const cors = require('cors');
const AudioServer = require('./servers/AudioServer');


const app = express();
app.use(cors())


// Guacamole Server
const guacdOptions = {
    host: '192.168.178.31',
    port: 4822
};

const clientOptions = {
    crypt: {
        cypher: 'AES-256-CBC',
        key: 'MySuperSecretKeyForParamsToken12'
    }
};

const guacHttpServer = http.createServer(app);
const guacServer = new GuacamoleLite(
    {guacHttpServer},
    guacdOptions,
    clientOptions,
);

guacHttpServer.listen(8000);


// Print Server
app.use(express.json())
app.use('/files', express.static('C:\\Users\\alexa\\Desktop\\Masterarbeit\\out'))
const printHttpServer = http.createServer(app);
const printServer = new PrintServer(printHttpServer, app)
setup(printServer)
printHttpServer.listen(8010, () => {
    console.log('Print Server is up.')
})

async function setup(printServer){
    await printServer.init();
}

// Sound Server
const audioHttpServer = http.createServer(app);
const audioServer = new AudioServer(audioHttpServer);
audioHttpServer.listen(8020, () => {
    console.log('Audio Server is up.')
})