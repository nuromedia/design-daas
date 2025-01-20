class PrintClient {
  constructor(config, token, id) {
    this.wsServerAdress = config.printerAPI;
    this.downloadAPI = config.fetchFileAPI;
    this.token = token;
    this.id = id;
    this._path = "";
    this._status = "not connected";
    this.onStatusChange = null;
    this.onPathReceived = null;
    this.onFile = this.downloadFile;
  }

  set path(path) {
    this._path = path;
    this.onPathReceived(path);
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

  connect() {
    this.socket = new WebSocket(
      `${this.wsServerAdress}?token=${this.token}&id=${this.id}`,
    );

    this.socket.onerror = () => {
      this.status = "error";
    };

    this.socket.onclose = () => {
      this.status = "connection closed";
    };

    // Prepare temp file
    this.currentFileName = "";
    this.currentFileChunks = [];

    // On Message
    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      const type = message.type;

      if (type === "status") {
        this.status = message.status;
      } else if (type === "printer_path") {
        this.path = message.printer_path;
        this.status = "printer is running";
      } else if (type === "file-begin") {
        this.currentFileName = message.name;
        this.currentFileType = message.mimetype;
      } else if (type === "file-chunk") {
        const data64 = message.data;

        let byteCharacters = atob(data64);
        let byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        let byteArray = new Uint8Array(byteNumbers);
        this.currentFileChunks.push(byteArray);
      } else if (type === "file-end") {
        const blob = new Blob(this.currentFileChunks, {
          type: this.currentFileType,
        });
        this.onFile(blob, this.currentFileName);
        this.currentFileChunks = [];
        this.currentFileName = [];
      } else {
        console.log("unknown message");
      }
    };
  }

  downloadFile = function (blob, filename) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  disconnect() {
    this.socket.close();
  }
}
export default PrintClient;

