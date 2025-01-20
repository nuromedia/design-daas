const WebSocket = require('ws');
const net = require('net');

const wss = new WebSocket.Server({ port: 9000 });

// WebSocket server
wss.on('connection', function connection(ws) {
    console.log('WebSocket client connected');
    ws.on('message', function incoming(message) {
        tcpClientSocket.write(message);
    });
});

// TCP socket client
const tcpClientSocket = new net.Socket();
tcpClientSocket.connect(8080, '192.168.178.28', function() {
    console.log('Connected to TCP socket server');
});

tcpClientSocket.on('data', function(data) {
    console.log('Received data from TCP socket server:', data.toString());
});

tcpClientSocket.on('close', function() {
    console.log('Connection to TCP socket server closed');
});
