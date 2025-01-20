class PrintClient{

    constructor(serverIP, serverPort, id){
        this.serverIP = serverIP;
        this.serverPort = serverPort;
        this.id = id;
        this._path = ''
        this._status = 'not connected';
        this.onStatusChange = null;
        this.onPathReceived = null;
        this.onFile = this.downloadFile;
    }

    set path(path) {
        this._path = path;
        this.onPathReceived(path)
    }

    get path() {
        return this.path;
    }

    set status(newStatus) {
        this._status = newStatus;
        if (this.onStatusChange) {
            this.onStatusChange(newStatus);
        }
    }

    get status() {
        return this._status;
    }

    connect(){
        this.socket = new WebSocket(`ws://${this.serverIP}:${this.serverPort}`);

        // When connected, send the printer ID
        this.socket.onopen = () => {
            this.status = 'connected'
            this.socket.send(this.id)
        }

        this.socket.onerror = () => {
            this.status = 'error'
        }

        this.socket.onclose = () => {
            this.status = 'connection closed'
        }

        // Invoked when a file path for downloading is received
        this.socket.onmessage = (m) => {
            const data = JSON.parse(m.data);
            if (data.printer_path) {
                this.path =  `http://${this.serverIP}:631/${data.printer_path}`
                this.status = 'printer is running'
            } else if (data.file_path) {
                const absPath = `http://${this.serverIP}:${this.serverPort}/` + data.file_path;
                console.log(absPath)
                //this.downloadFile(absPath);
                this.onFile(absPath);
            }
        }
    }

    disconnect(){
        this.socket.close();
    }

    downloadFile = function(path) {
        fetch(path)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = path.split('/').pop();
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error downloading file:', error));
    }
}
export default PrintClient;