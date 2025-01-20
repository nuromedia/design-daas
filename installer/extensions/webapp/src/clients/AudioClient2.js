class AudioClient {

    constructor(config, token, destination){
        this.token = token;
        this.destination = destination;
        this.wsServerAddress = config.microphoneAPI;

        this._status = 'not connected';
        this.onStatusChange = null;

        this.audioContext = null;
        this.scriptNode = null;
        this.source = null;
        this.mediaStream = null;
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
        this.status = 'connecting'
        this.socket = new WebSocket(`${this.wsServerAddress}?token=${this.token}&destination=${this.destination}`);

        this.socket.onopen = () => {
            this.status = 'connected to proxy'
        }

        this.socket.onerror = (e) => {
            this.status = 'error'
        }

        this.socket.onclose = () => {
            this.status = 'connection closed'
        }

        // Only invoked once when server is connected to the VM or failed to connect
        this.socket.onmessage = (message) => {
            //console.log('Audio client received: ' + message.data)
            if(message.data === 'connected')
                this.status = 'ready'
            else
                this.status = 'cannot reach remote audio server'
        }
    }

    disconnect(){
        this.socket.close();
        this.status = 'disconnected'
    }

    startRecording() {
        if(!(this.status === 'ready'))
            return

        navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
            this.mediaStream = stream;
            this.audioContext = new AudioContext();
            this.audioContext.resume();

            const targetSampleRate = 44100; // Target sample rate for resampling
            const LANCZOS_WINDOW_SIZE = 3;

            function sinc(x) {
                if (x === 0) return 1;
                const piX = Math.PI * x;
                return Math.sin(piX) / piX;
            }

            function lanczos(x, a) {
                if (-a < x && x < a) return sinc(x) * sinc(x / a);
                return 0;
            }

            function interpolateSample(audioData, t) {
                const index = (audioData.length - 1) * t;
                const start = Math.floor(index) - LANCZOS_WINDOW_SIZE + 1;
                const end = Math.floor(index) + LANCZOS_WINDOW_SIZE;
                let sum = 0;
                for (let i = start; i <= end; i++) {
                    sum += (audioData[i] || 0) * lanczos(index - i, LANCZOS_WINDOW_SIZE);
                }
                return sum;
            }

            function resampleAudioData(audioBuffer, targetSampleRate) {
                const inputSampleRate = audioBuffer.sampleRate;
                const resampleRatio = targetSampleRate / inputSampleRate;
                const length = Math.floor(audioBuffer.length * resampleRatio);
                const resampledData = new Float32Array(length);

                const inputChannelData = audioBuffer.getChannelData(0); // assuming mono
                for (let i = 0; i < length; i++) {
                    const t = i / (length - 1);
                    resampledData[i] = interpolateSample(inputChannelData, t);
                }

                return resampledData;
            }

            function onAudioCaptured(event) {
                const audioBuffer = event.inputBuffer;
                const resampledData = resampleAudioData(audioBuffer, targetSampleRate);
                const intData = new Int16Array(resampledData.length);
                for (let i = 0; i < resampledData.length; i++) {
                    intData[i] = Math.max(-0x7FFF, Math.min(0x7FFF, resampledData[i] * 0x7FFF)); // Scale to 16-bit range
                }
                // Send audio data over WebSocket connection
                this.socket.send(intData.buffer);
                console.log("Size: "+ intData.buffer.byteLength);
            }

            const scriptNode = this.audioContext.createScriptProcessor(2048, 1, 1);
            scriptNode.onaudioprocess = onAudioCaptured.bind(this);
            scriptNode.connect(this.audioContext.destination);

            const source = this.audioContext.createMediaStreamSource(stream);
            source.connect(scriptNode);
        });
    }

    stopRecording() {
        if (this.scriptNode) {
            this.scriptNode.disconnect();
            this.scriptNode = null;
        }
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
    }

}

export default AudioClient;
