class ResamplerWorklet {
  scriptNode = null;
  source = null;
  socket_audio = null;
  constructor() {
    this.scriptNode = null;
    this.source = null;
    this.socket_audio = null;
    this.targetSampleRate = 44100;
    this.window_size = 3;
  }
  connect(socket, sampleRate, window_size) {
    if (this.socket_audio !== null) return;
    this.targetSampleRate = sampleRate;
    this.window_size = window_size;
    this.socket_audio = socket;

    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.socket_audio.send(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        console.log("Recording stopped");
      };

      // Start recording
      mediaRecorder.start(1);
    });
  }
  disconnect() {
    if (this.scriptNode) {
      this.scriptNode.disconnect();
      this.scriptNode = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
    this.socket_audio = null;
  }
  onAudioCaptured(event) {
    if (this.socket_audio !== null) {
      console.log("CAPTURE: " + JSON.stringify(event.data));
      const audioBuffer = event.data;
      try {
        if (this.socket_audio !== null && event.data.size > 0) {
          this.socket_audio.send(audioBuffer);
        }
      } catch (Exception) {
        console.log("Error on sending audio data to socket");
      }
    }
  }
}

class Resampler {
  scriptNode = null;
  source = null;
  socket_audio = null;
  constructor() {
    this.scriptNode = null;
    this.source = null;
    this.socket_audio = null;
    this.targetSampleRate = 44100;
    this.window_size = 3;
  }
  connect(socket, sampleRate, window_size) {
    if (this.socket_audio !== null) return;
    this.targetSampleRate = sampleRate;
    this.window_size = window_size;
    this.socket_audio = socket;
    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      this.mediaStream = stream;
      this.audioContext = new AudioContext();
      this.audioContext.resume();
      this.scriptNode = this.audioContext.createScriptProcessor(2048, 1, 1);
      this.scriptNode.onaudioprocess = this.onAudioCaptured.bind(this);
      this.scriptNode.connect(this.audioContext.destination);
      this.source = this.audioContext.createMediaStreamSource(stream);
      this.source.connect(this.scriptNode);
    });
  }
  disconnect() {
    if (this.scriptNode) {
      this.scriptNode.disconnect();
      this.scriptNode = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
    this.socket_audio = null;
  }
  sinc(x) {
    if (x === 0) return 1;
    const piX = Math.PI * x;
    return Math.sin(piX) / piX;
  }
  lanczos(x, a) {
    if (-a < x && x < a) return this.sinc(x) * this.sinc(x / a);
    return 0;
  }
  interpolateSample(audioData, t) {
    const index = (audioData.length - 1) * t;
    const start = Math.floor(index) - this.window_size + 1;
    const end = Math.floor(index) + this.window_size;
    let sum = 0;
    for (let i = start; i <= end; i++) {
      sum += (audioData[i] || 0) * this.lanczos(index - i, this.window_size);
    }
    return sum;
  }
  resampleAudioData(audioBuffer, targetSampleRate) {
    const inputSampleRate = audioBuffer.sampleRate;
    const resampleRatio = targetSampleRate / inputSampleRate;
    const length = Math.floor(audioBuffer.length * resampleRatio);
    const resampledData = new Float32Array(length);
    const inputChannelData = audioBuffer.getChannelData(0);
    for (let i = 0; i < length; i++) {
      const t = i / (length - 1);
      resampledData[i] = this.interpolateSample(inputChannelData, t);
    }
    return resampledData;
  }
  onAudioCaptured(event) {
    if (this.socket_audio !== null) {
      const audioBuffer = event.inputBuffer;
      const resampledData = this.resampleAudioData(
        audioBuffer,
        this.targetSampleRate,
      );
      const intData = new Int16Array(resampledData.length);
      for (let i = 0; i < resampledData.length; i++) {
        intData[i] = Math.max(
          -0x7fff,
          Math.min(0x7fff, resampledData[i] * 0x7fff),
        );
      }
      try {
        this.socket_audio.send(intData.buffer);
      } catch (Exception) {
        console.log("Error on sending audio data to socket");
      }
    }
  }
}
class ProtocolExtensions {
  vnc = null;
  rdp = null;
  current = null;
  constructor(contype, backendUrl, token, userid) {
    this.id = userid;
    this.token = token;
    this.backendUrl = backendUrl;
    this.contype = contype;
    this.logging = true;
    this.backendUrl = this.backendUrl.replace("http://", "ws://");
    this.backendUrl = this.backendUrl.replace("https://", "wss://");
    if (contype === "rdp") {
      this.configRdp = {
        userid: this.id,
        token: this.token,
        logging: this.logging,
        samplingSize: 44100,
        codec: "audio/L16",
        channels_in: 1,
        channels_out: 1,
      };
      this.rdp = new RdpExtension(this.configRdp);
      this.current = this.rdp;
    } else if (contype === "sysvnc" || contype === "instvnc") {
      this.configVnc = {
        userid: this.id,
        token: this.token,
        logging: this.logging,
        samplingSize: 44100,
        windowSize: 3,
        url_print: this.backendUrl + "/extensions/printer_ws",
        url_audio: this.backendUrl + "/extensions/audio_ws",
      };
      this.vnc = new VncExtension(this.configVnc);
      this.current = this.vnc;
    }
  }
  async connect(client) {
    await this.current.connect(client);
  }
  disconnect() {
    this.current.disconnect();
  }
  async start_recording() {
    if (this.contype !== "rdp") {
      await this.vnc.start_recording();
    }
    return this.current.recording;
  }
  stop_recording() {
    if (this.contype !== "rdp") {
      this.vnc.stop_recording();
    }
    return true;
  }
  consume_events() {
    if (this.contype === "rdp") {
      this.current.client.onfile = this.current.onFile.bind(this.current);
    }
  }
  isConnectedRecorder() {
    return this.current.recording;
  }
  isConnectedAudio() {
    return this.current.connected_audio;
  }
  isConnectedPrinter() {
    return this.current.connected_printer;
  }
}
class ExtensionBase {
  type = "Unknown";
  client = null;
  recording = false;
  connected_audio = false;
  connected_printer = false;
  constructor(config, extensionType) {
    this.type = extensionType;
    this.config = config;
    this.client = null;
    this.log_info("Using " + this.type + " extension");
  }
  push_file_chunk(dataChunks, data64) {
    let byteCharacters = atob(data64);
    let byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    let byteArray = new Uint8Array(byteNumbers);
    dataChunks.push(byteArray);
    return dataChunks;
  }
  push_file_to_client(filename, dataChunks, mimetype) {
    const blob = new Blob(dataChunks, { type: mimetype });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.textContent = filename;
    document.ViewerLayout.debugView.addPrintFile({ foo: "foo" }, a, filename);
  }
  normalizeFilename(filename) {
    filename = this.removePrinterJobs(filename);
    filename = this.removeDoubledExtension(filename);
    filename = this.removeLibreOfficeTrailer(filename);
    return filename;
  }
  removePrinterJobs(filename) {
    const oldname = filename;
    var result = oldname;
    result = oldname.replace(/^(.*?)-job.*(\.pdf)$/, "$1$2");
    if (oldname !== result) {
      this.log_info("Removed printer jobs from filename '" + result + "'");
    }
    return result;
  }
  removeLibreOfficeTrailer(filename) {
    const oldname = filename;
    let result = oldname;
    const regex = /^(.*?)(\.\w{2,4})(?:__L)?(\.pdf)$/;
    result = oldname.replace(regex, "$1$2$3");
    if (oldname !== result) {
      this.log_info(
        "Removed LibreOffice trailer from filename: '" + result + "'",
      );
    }
    return result;
  }
  removeDoubledExtension(filename) {
    const oldname = filename;
    var result = oldname;
    if (oldname.endsWith(".pdf.pdf")) {
      result = oldname.slice(0, -4);
      this.log_info("Removed doubled extension from filename '" + result + "'");
    }
    return result;
  }

  log_info(msg) {
    if (this.config.logging === true) {
      console.log("EXT (" + this.type + "): " + msg);
    }
  }
  log_error(msg) {
    console.error("EXT (" + this.type + "): " + msg);
  }
}
class RdpExtension extends ExtensionBase {
  audioStreamRDP = null;
  recorder = null;
  constructor(config) {
    super(config, "rdp");
    this.audioStreamRDP = null;
    this.recorder = null;
  }
  async connect(client) {
    this.connected_audio = this.connect_audio(client);
    this.connected_printer = true;
    this.log_info("Connected extension");
  }
  disconnect() {
    this.audioStreamRDP.sendEnd();
    this.recording = false;
    this.connected_audio = false;
    this.connected_printer = false;
    this.log_info("Disconnected extension");
  }
  connect_audio(client) {
    this.client = client;
    const channelConf = this.getChannelConf();
    this.audioStreamRDP = this.client.createAudioStream(channelConf);
    this.log_info("Initialized audio stream");
    this.recorder = Guacamole.AudioRecorder.getInstance(
      this.audioStreamRDP,
      channelConf,
    );
    if (!this.recorder) {
      this.audioStreamRDP.sendEnd();
      this.recording = false;
    } else {
      this.recorder.onclose = this.recordAudio;
      this.recording = true;
    }
    this.log_info("Initialized audio recorder");
    return this.recording === true;
  }
  onFile(stream, mimetype, filename) {
    let dataChunks = [];
    filename = this.normalizeFilename(filename);
    stream.onblob = (data64) => {
      dataChunks = this.push_file_chunk(dataChunks, data64);
      stream.sendAck("OK", Guacamole.Status.Code.SUCCESS);
    };
    stream.onend = () => {
      this.push_file_to_client(filename, dataChunks, mimetype);
      stream.sendAck("OK", Guacamole.Status.Code.SUCCESS);
    };
    this.onFileBegin(filename);
    stream.sendAck("OK", Guacamole.Status.Code.SUCCESS);
  }
  onFileBegin(filename) {
    this.log_info("Filetransfer initiated for '" + filename + "'");
  }
  getChannelConf() {
    return (
      this.config.codec +
      ";rate=" +
      this.config.samplingSize +
      ",channels=" +
      (this.config.channels_in + this.config.channels_out)
    );
  }
}
class VncExtension extends ExtensionBase {
  resampler = null;
  socket_audio = null;
  socket_printer = null;
  currentFileChunks = {};
  constructor(config) {
    super(config, "vnc");
    this.resampler = null;
    this.socket_audio = null;
    this.socket_printer = null;
    this.currentFileChunks = {};
  }
  async connect(client) {
    this.client = client;
    this.connected_printer = this.connect_printer();
  }
  async connect_audio() {
    const url = `${this.config.url_audio}/${this.config.token}`;
    this.socket_audio = new WebSocket(url);
    this.socket_audio.onerror = this.onAudioError.bind(this);
    this.socket_audio.onclose = this.onAudioClosed.bind(this);
    this.socket_audio.onopen = this.onAudioOpen.bind(this);
    this.socket_audio.onmessage = this.onAudioMessage.bind(this);
    this.resampler = new Resampler();
    await this.resampler.connect(
      this.socket_audio,
      this.config.samplingSize,
      this.config.windowSize,
    );
    this.log_info("Started resampling service");
    this.recording = true;
    this.connected_audio = this.recording === true;
    this.log_info("Connected audio extension");
    return this.connected_audio;
  }
  connect_printer() {
    const url = `${this.config.url_print}/${this.config.token}`;
    this.socket_printer = new WebSocket(url);
    this.socket_printer.onerror = this.onPrinterError.bind(this);
    this.socket_printer.onclose = this.onPrinterClosed.bind(this);
    this.socket_printer.onmessage = this.onMessage.bind(this);
    this.connected_printer = true;
    this.log_info("Connected printer extension");
    return this.connected_printer;
  }
  disconnect() {
    this.stop_recording();
    this.disconnect_audio();
    this.disconnect_printer();
  }
  disconnect_printer() {
    if (this.socket_printer !== null) {
      this.socket_printer.send("close");
      this.socket_printer.close();
      this.socket_printer = null;
    }
    this.connected_printer = false;
    this.log_info("Disconnected printer");
  }
  disconnect_audio() {
    if (this.socket_audio !== null) {
      this.socket_audio.send("close");
      this.socket_audio.close();
      this.socket_audio = null;
    }
    this.connected_audio = false;
    this.log_info("Disconnected audio");
  }
  async start_recording() {
    this.log_info("Starting microphone service");
    await this.connect_audio();
    return this.recording;
  }
  stop_recording() {
    if (this.resampler !== null) {
      this.resampler.disconnect();
    }
    this.disconnect_audio();
    this.recording = false;
    return true;
  }
  onMessage(event) {
    const message = JSON.parse(event.data);
    const type = message.type;
    if (type === "file-begin") {
      this.onFileBegin(message.name);
    } else if (type === "file-chunk") {
      this.onFileChunk(message);
    } else if (type === "file-end") {
      this.onFileEnd(message);
    }
  }
  onFileBegin(filename) {
    filename = this.normalizeFilename(filename);
    this.log_info("Filetransfer initiated for '" + filename + "'");
  }
  onFileChunk(message) {
    const data64 = message.data;
    var chunks = this.currentFileChunks[message.randid];
    if (typeof chunks === "undefined") {
      chunks = [];
    }
    chunks = this.push_file_chunk(chunks, data64);
    this.currentFileChunks[message.randid] = chunks;
  }
  onFileEnd(message) {
    const filename = this.normalizeFilename(message.name);
    this.push_file_to_client(
      filename,
      this.currentFileChunks[message.randid],
      message.mimetype,
    );
    this.currentFileChunks[message.randid] = [];
  }
  onAudioMessage(message) {
    this.log_info("Audio client received: " + message.data);
    if (message.data === "Connected") this.log_info("Audio service connected");
    else this.log_error("Audio service not available");
  }
  onAudioOpen() {
    this.log_info("Audio stream opened");
  }
  onAudioClosed() {
    this.log_info("Audio socket closed");
  }
  onAudioError() {
    this.log_error("Audio socket terminated");
  }
  onPrinterClosed() {
    this.log_info("Printer socket closed");
  }
  onPrinterError() {
    this.log_error("Printer socket terminated");
  }
}
