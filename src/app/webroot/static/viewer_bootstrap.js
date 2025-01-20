class BootStrapper {
  configViewer = null;
  configInstance = null;
  instanceInfo = null;
  viewerLayout = null;
  reconnect = true;

  constructor(configViewer, configInstance) {
    document.Bootstrap = this;
    this.configViewer = configViewer;
    this.configInstance = configInstance;
  }
  async init() {
    this.viewerLayout = new ViewerLayout(this.configInstance);
    await this.viewerLayout.init();
    this.viewerGuac = new GuacamoleWrapper(this.configInstance);
    this.viewerGuac.setHandlers(
      this.cb_client_connected.bind(this),
      this.cb_client_disconnected.bind(this),
      this.cb_client_sync.bind(this),
    );
    // console.log("CFG-Viewer  : " + this.configViewer.str());
    // console.log("CFG-Instance: " + this.configInstance.str());

    var sz = null;
    if (this.configInstance.resolution === "max") {
      sz = "max";
    } else {
      sz = new Size(0, 0);
      sz.fromString(this.configInstance.resolution);
    }
    this.viewerLayout.resizeView(sz);
    this.viewerLayout.handleScaleChange();
    this.bootstrap_components();
  }
  handleResize(entries) {
    for (let entry of entries) {
      const { width, height } = entry.contentRect;
      this.viewerLayout.updateMaxSize();
      console.log(
        `VIEWER   : Element size: ${this.viewerLayout.maxSize.width}px x ${this.viewerLayout.maxSize.height}px`,
      );
      var sz = null;
      if (this.configInstance.resolution === "max") {
        sz = "max";
      } else {
        sz = new Size(0, 0);
        sz.fromString(this.configInstance.resolution);
      }
      this.viewerLayout.resizeView(sz);
      this.viewerLayout.handleResolutionChange();
      this.viewerLayout.handleResizeChange();
      this.viewerLayout.handleScaleChange();
    }
  }
  debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  async bootstrap_components() {
    this.viewerLayout.statusView.setStatusWait();
    await this.updateInstanceInfo();
    const resizableElement = document.body;
    const debouncedHandleResize = this.debounce(
      this.handleResize.bind(this),
      300,
    );

    const resizeObserver = new ResizeObserver(debouncedHandleResize);
    resizeObserver.observe(resizableElement);

    while (true) {
      if (this.checkRunModes() === false) {
        await this.updateInstanceInfo();
      }
      await this.sleep(500);
      if (this.needsConnect() === true) {
        if (this.viewerGuac.disconnects > this.configViewer.reconnect_max) {
          await this.sleep(this.configViewer.reconnect_delayed_ms);
        }
        this.conditionalConnect();
      } else {
        await this.sleep(100);
      }
    }
  }
  conditionalConnect() {
    var connect = false;
    if (this.reconnect === true) {
      const mode = this.instanceInfo.instanceInfo.parsedMode;
      const extmode = this.instanceInfo.instanceInfo.parsedModeExtended;
      if (mode === "run-app") {
        if (extmode === "done") {
          connect = true;
        } else {
          this.viewerLayout.statusView.setStatusWait();
        }
      } else {
        connect = true;
      }
    }
    if (connect === true) {
      const disconnects = this.viewerGuac.disconnects;
      if (disconnects === 0) {
        this.viewerLayout.statusView.setStatusConnecting();
      }
      this.viewerGuac.connect(this.configInstance);
    }
  }
  async updateInstanceInfo() {
    this.instanceInfo = await this.getInstanceState(this.configInstance, 1, 1);
    this.viewerLayout.setInfo(this.instanceInfo);
    if (this.instanceInfo !== null && this.instanceInfo.instanceInfo !== null) {
      const info = this.instanceInfo.instanceInfo;
      this.viewerLayout.overlay.showOverlayByMode(
        info.parsedMode,
        info.parsedModeExtended,
      );
    }
  }
  async getInstanceState(configInstance, retriesPing, retriesInfo) {
    var success = false;
    var instanceInfo = {};
    const pingInfo = await this.pingInstance(configInstance, retriesPing);
    if (pingInfo !== false) {
      var info = await this.getInstanceInfo(
        configInstance,
        retriesInfo,
        this.configViewer.resolution_check_init,
      );
      if (info.success === true) {
        var msg = info.parsedModeExtended;
        if (info.parsedModeExtended === "done") {
          msg = "app running";
        }
        this.viewerLayout.statusView.updateHint(msg);
        this.viewerLayout.overlay.setOverlayHint("Mode: " + msg);
      }
      instanceInfo = info;
      success = info.success;
      const result = {
        success: success,
        pingInfo: pingInfo,
        instanceInfo: info,
      };
      this.viewerLayout.setInfo(result);
      return result;
    }
    const result = {
      success: false,
      pingInfo: null,
      instanceInfo: null,
    };
    this.viewerLayout.setInfo(result);
    return result;
  }

  async pingInstance(configInstance, retries) {
    const svc = new BackendService(configInstance.backendUrl, retries);
    try {
      const data = await svc.checkInstance(
        configInstance.instance,
        configInstance.token,
      );
      if (
        data["response_data"] !== "undefined" &&
        data["response_data"]["available"] !== "undefined" &&
        data["response_data"]["booted"] !== "undefined" &&
        data["response_data"]["connection"] !== "undefined"
      ) {
        return data["response_data"];
      }
    } catch (error) {
      console.log("Instance check unsuccessful");
    }
    return false;
  }
  async getInstanceInfo(configInstance, retries, resolutions) {
    const svc = new BackendService(
      configInstance.backendUrl,
      retries,
      resolutions,
    );
    try {
      const data = await svc.getInfo(
        configInstance.instance,
        configInstance.token,
      );
      // console.log("Data: " + JSON.stringify(data));
      if (data["response_data"] !== "undefined") {
        var parsedResolutions = [];
        var parsedMode = {};
        var parsedModeExtended = {};
        if (data["response_data"]["resolutions"] !== "undefined") {
          var resolutionData = data["response_data"]["resolutions"];
          var inputStr = resolutionData.slice(1, -1);
          if (inputStr.includes(",")) {
            if (inputStr.includes("), (")) {
              let items = inputStr.split("), (");
              items.unshift("max");
              parsedResolutions = items.map((item) =>
                item.replace(/[()]/g, "").trim().replace(", ", "x"),
              );
            } else {
              parsedResolutions = resolutionData
                .replace(/[()]/g, "")
                .trim()
                .replace(", ", "x");
            }
          }
          var testdata = data["response_data"];
          if (testdata["mode"] !== "undefined") {
            parsedMode = testdata["mode"];
            if (testdata["mode_extended"] !== "undefined") {
              parsedModeExtended = testdata["mode_extended"];
              if (testdata["obj"] !== "undefined") {
                var parsedObject = testdata["obj"];
                if (testdata["env"] !== "undefined") {
                  var parsedEnv = testdata["env"];
                  if (testdata["app"] !== "undefined") {
                    var parsedApp = testdata["app"];
                    if (testdata["stats"] !== "undefined") {
                      var parsedStats = testdata["stats"];
                      return {
                        success: true,
                        obj: parsedObject,
                        env: parsedEnv,
                        app: parsedApp,
                        stats: parsedStats,
                        parsedMode: parsedMode,
                        parsedModeExtended: parsedModeExtended,
                        resolutions: parsedResolutions,
                      };
                    }
                  }
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.log("Instance check unsuccessful");
    }
    return {
      success: false,
    };
  }
  needsConnect() {
    if (
      this.viewerGuac.isConnected === false &&
      this.viewerGuac.isConnecting === false
    ) {
      return true;
    }
    return false;
  }
  checkRunModes() {
    if (
      this.instanceInfo !== null &&
      this.instanceInfo.instanceInfo !== null &&
      this.instanceInfo.instanceInfo.parsedMode === "run-app" &&
      this.instanceInfo.instanceInfo.parsedModeExtended === "done"
    ) {
      return true;
    }
    return false;
  }
  checkAppMode() {
    if (
      this.instanceInfo !== null &&
      this.instanceInfo.instanceInfo !== null &&
      this.instanceInfo.instanceInfo.parsedMode === "run-app"
    ) {
      return true;
    }
    return false;
  }
  async cb_client_connected() {
    this.viewerLayout.statusView.setStatusConnected();
    this.viewerLayout.showStatus();
  }
  async cb_client_disconnected(error) {
    if (this.checkAppMode() === true) {
      const disconnects = this.viewerGuac.disconnects;
      if (disconnects > 0 && disconnects <= this.configViewer.reconnect_max) {
        this.viewerLayout.statusView.setStatusReconnect(
          this.viewerGuac.disconnects,
        );
      } else if (disconnects > this.configViewer.reconnect_max) {
        this.viewerLayout.statusView.setStatusDelayed(
          this.viewerGuac.disconnects,
        );
      }
    } else {
      this.viewerLayout.statusView.setStatusReconnect(0);
    }
    this.viewerLayout.showStatus();
  }
  async cb_client_sync() {
    // this.viewerLayout.showClient();
    setTimeout(
      async function () {
        this.viewerLayout.showClient();
        await this.updateInstanceInfo();
      }.bind(this),
      250,
    );
  }
  handleReconnect(error) {}
  async sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
