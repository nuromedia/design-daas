import Guacamole from 'guacamole-common-js'

class RDPClient{

    constructor(client){
        this.client = client;
        this.audioStreamRDP = null;
        this.recorder = null;
        this.client.onfile = this.downloadFile;
        this.recordAudio();

    }

    recordAudio = () => {
        this.audioStreamRDP = this.client.createAudioStream("audio/L16;rate=44100,channels=2");        
        this.recorder = Guacamole.AudioRecorder.getInstance(this.audioStreamRDP, "audio/L16;rate=44100,channels=2"); 
        
        if(!this.recorder)
            this.audioStreamRDP.sendEnd();
        else 
            this.recorder.onclose = this.recordAudio;
    }


    downloadFile = (stream, mimetype, filename) => {
        // Remove dublicate .pdf
        if(filename.endsWith('.pdf.pdf')){
            filename = filename.slice(0, -4)
        }

        let dataChunks = [];
        stream.sendAck('OK', Guacamole.Status.Code.SUCCESS);
        
        // Collect all chunks
        stream.onblob = (data64) => {
            // Decode base64 data chunk
            let byteCharacters = atob(data64);
            let byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            let byteArray = new Uint8Array(byteNumbers);
            dataChunks.push(byteArray);
            
            stream.sendAck('OK', Guacamole.Status.Code.SUCCESS);
        };
        
        // Connect the chunks to a Blob and download the file
        stream.onend = () => {
            stream.sendAck('OK', Guacamole.Status.Code.SUCCESS);
    
            const blob = new Blob(dataChunks, { type: mimetype });

            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        };
    }

}
export default RDPClient;