class DisplayWrapper {
  client = null;
  mouse = null;
  keyboard = null;
  touch = null;
  display = null;
  displayElement = null;
  isInitialized = false;
  isMouseHovering = false;
  isScaled = false;
  nativeDisplaySize = null;
  currentDisplaySize = null;
  currentDisplayScale = 1;
  container = null;
  guacFirstDiv = null;
  guacFirstCanvas = null;

  constructor(clientView, client, display) {
    this.client = client;
    this.display = display;
    this.container = document.getElementById(clientView);
    this.isInitialized = this.initialize();
  }
  initialize() {
    if (
      this.display !== "undefined" &&
      this.display !== null &&
      this.container !== null
    ) {
      this.displayElement = this.display.getElement();
      this.guacFirstDiv = this.displayElement.firstChild;
      if (this.display !== "undefined" && this.guacFirstDiv !== null) {
        this.guacFirstDiv.className = "guac-div-viewer";
        this.guacFirstDiv.id = "guac-div-viewer";
        this.guacFirstDiv.style.zIndex = "1";
        this.guacFirstCanvas = this.guacFirstDiv.querySelector("canvas");
        if (this.guacFirstCanvas !== null) {
          this.guacFirstCanvas.className = "guac-canvas-viewer";
          this.guacFirstCanvas.id = "guac-canvas-viewer";
          this.guacFirstCanvas.style.zIndex = "1";
          const newSize = new Size(
            this.displayElement.style.width,
            this.displayElement.style.height,
          );
          if (newSize.hasExtend === true) {
            this.nativeDisplaySize = newSize;
            this.currentDisplaySize = newSize;
            this.isInitialized = this.initialize_devices();
            if (this.isInitialized === true) {
              console.log("DISPLAY  : Initialzed with Size: " + newSize.str());
              return true;
            } else {
              console.log("DISPLAY: Devices NOT initialized.");
            }
          } else {
            console.log(
              "DISPLAY  : Display NOT ininitialized. Size was: " +
                newSize.str(),
            );
          }
        }
      }
    } else {
      console.log(
        "DISPLAY  : Display NOT ininitialized. Display was: " + this.display,
      );
    }
    return false;
  }
  initialize_devices() {
    if (
      this.container !== null &&
      this.client !== null &&
      this.guacFirstDiv !== null &&
      this.guacFirstCanvas !== null
    ) {
      this.mouse = new Guacamole.Mouse(this.guacFirstCanvas);
      this.touch = new Guacamole.Touch(this.guacFirstCanvas);
      this.keyboard = new Guacamole.Keyboard();
      this.keyboard.listenTo(this.container);
      this.mouse.on("mousemove", this.cb_mouse_event.bind(this));
      this.mouse.on("mouseup", this.cb_mouse_up_event.bind(this));
      this.mouse.on("mousedown", this.cb_mouse_down_event.bind(this));
      this.mouse.on("mouseout", this.cb_mouse_out_event.bind(this));
      this.touch.on("mousemove", this.cb_touch_event.bind(this));
      // this.touch.on("touchstart", this.cb_touch_event.bind(this));
      // this.touch.on("touchend", this.cb_touch_event.bind(this));
      this.keyboard.onkeyup = this.cb_keyboard_keyup.bind(this);
      this.keyboard.onkeydown = this.cb_keyboard_keydown.bind(this);
      this.client.onaudio = function (stream) {
        var audio = new Guacamole.AudioPlayer(stream);
        audio.play();
      };
      return true;
    }
    return false;
  }
  cb_mouse_event(e) {
    if (this.setMouseHover()) {
      if (this.isInitialized === true) {
        if (this.isScaled === true) {
          e.state.x *= 1 / this.currentDisplayScale;
          e.state.y *= 1 / this.currentDisplayScale;
        }
      }
      this.client.sendMouseState(e.state, false);
      // e.preventDefault();
    }
  }
  cb_mouse_up_event(e) {
    this.client.sendMouseState(e.state, false);
  }
  cb_mouse_down_event(e) {
    this.client.sendMouseState(e.state, false);
  }
  cb_mouse_out_event() {
    this.isMouseHovering = false;
  }
  cb_touch_event(e) {
    this.client.sendTouchState(e.state, true);
  }
  cb_keyboard_keyup(keysym) {
    this.client.sendKeyEvent(0, keysym);
  }
  cb_keyboard_keydown(keysym) {
    if (this.isMouseHovering) {
      this.client.sendKeyEvent(1, keysym);
    }
  }
  setMouseHover() {
    if (this.isMouseHovering === false) {
      setTimeout(
        function () {
          this.guacFirstCanvas.setAttribute("tabindex", "0");
          this.guacFirstCanvas.focus();
        }.bind(this),
        1,
      );
      this.isMouseHovering = true;
    }
    return this.isMouseHovering;
  }
  scaleSize(sizeTarget) {
    if (this.isInitialized === true) {
      this.currentDisplayScale = 1;
      this.currentDisplaySize = this.nativeDisplaySize;
      this.display.scale(this.currentDisplayScale);
      this.isScaled = false;

      const sizeDisplay = this.currentDisplaySize;
      if (sizeDisplay.equals(sizeTarget) === false) {
        var fw = sizeTarget.width / sizeDisplay.width;
        var fh = sizeTarget.height / sizeDisplay.height;

        var newScale =
          fw < 1
            ? (newScale = Math.min(fw, fh))
            : (newScale = Math.min(fw, fh));
        if (newScale != 1) {
          this.currentDisplayScale = newScale;
          this.display.scale(this.currentDisplayScale);
          this.currentDisplaySize = new Size(
            this.displayElement.style.width,
            this.displayElement.style.height,
          );
          this.isScaled = true;
        }
      }
    }
  }
  unscale() {
    if (this.isInitialized === true) {
      this.currentDisplayScale = 1;
      this.display.scale(this.currentDisplayScale);
      this.currentDisplaySize = new Size(
        this.displayElement.style.width,
        this.displayElement.style.height,
      );
      this.isScaled = false;
    }
  }
}

class GuacamoleWrapper {
  cfg = null;
  extensions = null;
  tunnel = null;
  tunnelParams = null;
  client = null;
  onsync = null;
  onconnect = null;
  ondisconnect = null;
  container = null;
  displayWrapper = null;
  disconnects = 0;
  isConnected = false;
  isTunnelOpen = false;
  isSynced = false;
  isConnecting = false;
  isDisconnecting = false;

  constructor(configInstance) {
    this.cfg = configInstance;
    this.extensions = new ProtocolExtensions(
      this.cfg.contype,
      this.cfg.backendUrl,
      this.cfg.token,
      this.cfg.owner,
    );
    this.container = document.getElementById("client-view");
    this.log_info("CLIENT   : Client initialized");
  }
  connect(cfg) {
    var result = false;
    this.log_info("Connect with args: " + cfg.str());
    this.extensions = new ProtocolExtensions(
      this.cfg.contype,
      this.cfg.backendUrl,
      this.cfg.token,
      this.cfg.owner,
    );
    this.cfg = cfg;
    this.isConnected = false;
    this.isTunnelOpen = false;
    this.isSynced = false;
    this.isConnecting = true;
    this.createTunnel();
    this.create_tunnel_params();
    this.create_client(this.tunnel);
    if (this.tunnelParams !== null && this.client != null) {
      this.client.connect(this.tunnelParams.toString());
      result = true;
    }
    return result;
  }
  disconnect() {
    if (this.client !== null && this.isDisconnecting === false) {
      this.isDisconnecting = true;
      this.client.disconnect();
      this.isSynced = false;
      this.isTunnelOpen = false;
      this.isConnected = false;
      this.isConnecting = false;
      this.isDisconnecting = false;
    }
    this.disconnect_extensions();
  }
  setHandlers(conHandler, disconHandler, syncHandler) {
    this.onconnect = conHandler;
    this.ondisconnect = disconHandler;
    this.onsync = syncHandler;
  }
  unsetHandlers() {
    this.onsync = null;
    this.onconnect = null;
    this.ondisconnect = null;
  }
  createTunnel() {
    this.tunnel = new Guacamole.WebSocketTunnel(this.cfg.tunnelUrl);
    this.log_info("TUNNEL   : Tunnel created: " + this.cfg.instance);
    return this.tunnel;
  }
  create_tunnel_params() {
    const targetSize = this.getTargetSize();
    const lossless = this.cfg.lossless === true ? "true" : "false";

    this.tunnelParams = new URLSearchParams();
    this.tunnelParams.append("GUAC_WIDTH", targetSize.width);
    this.tunnelParams.append("GUAC_HEIGHT", targetSize.height);
    this.tunnelParams.append("GUAC_DPI", this.cfg.dpi);
    this.tunnelParams.append("GUAC_COLORDEPTH", this.cfg.colors);
    this.tunnelParams.append("GUAC_LOSSLESS", lossless);
    this.tunnelParams.append("GUAC_AUTORETRY", 1);
    this.tunnelParams.append("GUAC_KEYBOARD", "de-de-qwertz");
    this.tunnelParams.append("GUAC_RESIZEMETHOD", "reconnect");
    this.tunnelParams.append("GUAC_AUDIO", "audio/L16");
    this.tunnelParams.append("GUAC_AUDIO_INPUT", "true");
    this.tunnelParams.append("GUAC_ENABLE_PRINTING", "true");
    this.log_info("TUNNEL   : Params created");
    return this.tunnelParams;
  }
  getTargetSize() {
    var size = document.ViewerLayout.currentSize;
    if (size === "max") {
      size = document.ViewerLayout.viewSize;
    }
    return size;
  }
  create_client(tunnel) {
    this.client = new Guacamole.Client(tunnel);
    this.client.connected = false;
    this.client.onerror = this.cb_client_error.bind(this);
    this.client.onsync = this.cb_client_onsync.bind(this);
    this.client.onstatechange = this.cb_client_onstatechange.bind(this);
    return this.client;
  }
  create_new_display() {
    const display = this.client.getDisplay();
    this.displayWrapper = new DisplayWrapper(
      "client-view",
      this.client,
      display,
    );
    if (this.displayWrapper.isInitialized === true) {
      this.container.appendChild(this.displayWrapper.displayElement);
      var sizeTarget = this.getTargetSize();
      var sizeDisplay = this.displayWrapper.nativeDisplaySize;
      const tools = new ResolutionTools();
      const isNative = tools.isNativeResolution(
        sizeDisplay,
        document.ViewerLayout.resolutions,
      );
      if (isNative == false) {
        // const perfSize = tools.findNativeResolution(
        //   sizeTarget,
        //   document.ViewerLayout.resolutions,
        // );
        // const diff = sizeDisplay.diff(perfSize);
        // console.log("Scale: " + this.displayWrapper.currentDisplayScale);
        this.displayWrapper.scaleSize(sizeTarget);
        // console.log("Scale: " + this.displayWrapper.currentDisplayScale);
        // console.log("non-native resolution: " + sizeDisplay.toString());
        // console.log("DIFF       resolution: " + diff.toString());
      }
      document.ViewerLayout.handleScaleChange();
      document.ViewerLayout.handleMousepointer();
      return true;
    }
    return false;
  }
  cb_client_onstatechange(state) {
    if (state == Guacamole.Client.State.CONNECTED) {
      this.isConnecting = false;
      this.isConnected = true;
      this.log_info("CLIENT   : CONNECTED!");
      this.disconnects = 0;
      this.onconnect();
    }
    if (state == Guacamole.Client.State.DISCONNECTED) {
      this.container.innerHTML = "";
      this.isConnecting = false;
      this.isConnected = false;
      this.disconnect();
      this.disconnects++;
      this.ondisconnect({ code: 519, status: "Disconnected" });
      this.log_info("CLIENT   : DISCONNECTED!");
    }
  }
  cb_client_error(error) {
    if (typeof error !== "undefined") {
      this.log_info("CLIENT   : Client error " + error.code);
      this.ondisconnect(error);
    }
  }
  cb_client_onsync() {
    if (this.isSynced === false) {
      this.isSynced = this.create_new_display();
      if (this.isSynced === true && this.onsync !== null) {
        this.connect_extensions();
        this.onsync();
      }
    }
  }
  connect_extensions() {
    this.log_info("Extensions connect with: " + this.cfg.str());
    this.extensions.connect(this.client);
    this.extensions.consume_events();
  }
  disconnect_extensions() {
    this.extensions.disconnect();
  }
  async start_recording() {
    return await this.extensions.start_recording();
  }
  stop_recording() {
    return this.extensions.stop_recording();
  }
  log_info(msg) {
    console.log(msg);
    document.ViewerLayout.debugView.addLogElement(msg);
  }
  log_error(msg) {
    console.error(msg);
  }
}
