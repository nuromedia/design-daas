class ViewerLayout {
  constructor(configInstance) {
    document.ViewerLayout = this;
    this.configInstance = configInstance;
    this.initialized = false;
    this.currentSize = "max";
    this.currentView = "status";
    this.resolutions = [];
    this.contypes = [];
    this.isMaximized = true;
    this.maxSize = this.getMaxSize();
    this.viewSize = this.getViewSize();
    this.statusView = new StatusView("status-view", "mainview-container");
    this.clientView = new ClientView("client-view", "mainview-container");
    this.debugView = new DebugView("debug-view", "mainview-container");
    this.overlay = new Overlay("overlay", "overlay-container");
    this.sidebar = new Sidebar("sidebar", "sidebar-container");
    this.topbar = new Topbar("topbar", "topbar-container");
    this.initialized = false;
  }

  async init() {
    this.overlay.buildView();
    await this.sidebar.buildView();
    this.topbar.buildView();
    this.statusView.buildView();
    this.clientView.buildView();
    this.debugView.buildView();
    this.showStatus();
    this.sidebar.resInfo.setResolutions(
      this.currentSize,
      this.maxSize,
      new Size(0, 0),
    );
    this.sidebar.conInfo.setModes("none", "none");
    this.sidebar.conInfo.setStates("red", "red", "red", "red");
    this.populateResolutions([
      "max",
      "1920x1080",
      "1600x1200",
      "1680x1050",
      "1280x800",
      "1024x768",
      "800x600",
    ]);
    console.log(this.configInstance.str());
    var contypes = [];
    if (this.configInstance.isvm === true) {
      contypes.push("sysvnc");
      contypes.push("instvnc");
      if (this.configInstance.iswin === true) {
        contypes.push("rdp");
      }
    } else {
      contypes.push("instvnc");
    }
    this.poupulateContypes(contypes);
    window.addEventListener("resize", () => this.updateMaxSize());
    this.handleShadow();

    return true;
  }

  getMaxSize() {
    return new Size(window.innerWidth, window.innerHeight);
  }
  getViewSize() {
    var ox =
      this.maxSize.width -
      parseFloat(this.readCSSVariable("--view-offset-left")) -
      parseFloat(this.readCSSVariable("--view-offset-right"));
    var oy =
      this.maxSize.height -
      parseFloat(this.readCSSVariable("--view-offset-top")) -
      parseFloat(this.readCSSVariable("--view-offset-bottom"));
    return new Size(ox, oy);
  }
  updateMaxSize() {
    this.maxSize = new Size(
      Math.floor(window.innerWidth),
      Math.floor(window.innerHeight),
    );
  }

  handleResolutionChange() {
    const select = document.getElementById("resolutionSelect");
    const sz = new Size(0, 0);
    if (select.value === "max") {
      this.resizeView("max");
    } else {
      sz.fromString(select.value);
      this.resizeView(sz);
    }
    this.sidebar.resInfo.setResolutions(
      this.currentSize,
      this.maxSize,
      new Size(0, 0),
    );
    this.handleResizeChange();
    this.handleScaleChange();
    this.handleScrollbars();
  }
  async handleContypeChange(value) {
    console.log("Wants Contype change");
    document.Bootstrap.configInstance.contype = value;
    this.setScreen(document.Bootstrap.configInstance, 1);
    document.Bootstrap.reconnect = true;
    document.Bootstrap.viewerGuac.disconnect();
  }
  handleResizeChange() {
    const checkbox = document.getElementById("resolutionResize");
    if (
      typeof document.Bootstrap.viewerGuac !== "undefined" &&
      document.Bootstrap.viewerGuac !== null &&
      document.Bootstrap.viewerGuac.displayWrapper !== null
    ) {
      if (checkbox.checked === true) {
        const tools = new ResolutionTools();
        var newSize;
        if (this.isMaximized) {
          newSize = this.viewSize;
        } else {
          newSize = this.currentSize;
        }
        // console.log("NEWSIZE: " + newSize.str());

        const perfectSize = tools.findNativeResolution(
          newSize,
          this.resolutions,
        );
        // console.log("PERF  : " + perfectSize.str());
        const displaySize =
          document.Bootstrap.viewerGuac.displayWrapper.currentDisplaySize;
        // console.log("NATIVE: " + displaySize.str());

        if (displaySize !== null) {
          const diff = displaySize.diff(this.viewSize);
          // console.log("DIFF  : " + diff.str());
          document.Bootstrap.viewerGuac.displayWrapper.unscale();
          document.Bootstrap.viewerGuac.client.sendSize(
            perfectSize.width,
            perfectSize.height,
          );
          this.statusView.setStatusConnecting();
          this.showStatus();
          var waitTime = 1500;
          const cfg = document.Bootstrap.configInstance;
          if (cfg.isvm === true && cfg.iswin === true) {
            waitTime = 1500;
          } else if (cfg.isvm === true && cfg.iswin === false) {
            waitTime = 400;
          } else {
            waitTime = 1000;
          }
          console.log(
            "Sizechange! Waiting for resolution change: " + waitTime + "ms",
          );
          // document.Bootstrap.viewerGuac.client.sendSize(1280, 800);

          setTimeout(function () {
            document.Bootstrap.viewerGuac.displayWrapper.unscale();
            document.Bootstrap.viewerGuac.client.disconnect();
            document.Bootstrap.viewerGuac.client.connect();
          }, waitTime);
          if (
            displaySize.width < perfectSize.width ||
            displaySize.height < perfectSize.height
          ) {
          }
        }
      }
    }
  }
  handleScaleChange() {
    const checkbox = document.getElementById("resolutionScale");
    if (this.hasDisplay() === true) {
      var newSize;
      if (this.isMaximized) {
        newSize = this.viewSize;
      } else {
        newSize = this.currentSize;
      }
      if (checkbox.checked === true) {
        document.Bootstrap.viewerGuac.displayWrapper.scaleSize(newSize);
      } else {
        document.Bootstrap.viewerGuac.displayWrapper.unscale();
      }
      this.setInfo(document.Bootstrap.instanceInfo);
    }
  }
  handleMousepointer() {
    const mainview = document.getElementById("mainview-container");
    mainview.classList.add("mainview-localcursor");
    if (document.Bootstrap.configInstance.isvm === false) {
      //mainview.classList.add("mainview-localcursor");
    } else {
      //mainview.classList.remove("mainview-localcursor");
    }
  }
  handleScrollbars() {
    const mainview = document.getElementById("mainview-container");
    // if (mainview.clientWidth >= this.maxSize.width) {
    //   mainview.classList.remove("noscroll");
    // } else {
    //   mainview.classList.add("noscroll");
    // }
    const clientview = document.getElementById("client-view");
    if (this.hasDisplay() === true) {
      const displaySize =
        document.Bootstrap.viewerGuac.displayWrapper.currentDisplaySize;
      if (
        displaySize.width > this.maxSize.width ||
        displaySize.height > this.maxSize.height
      ) {
        clientview.classList.remove("noscroll-client");
        mainview.classList.add("oversized");
        mainview.classList.remove("noscroll-main");
      } else {
        clientview.classList.add("noscroll-client");
        mainview.classList.remove("oversized");
        mainview.classList.add("noscroll-main");
      }
    } else {
      mainview.classList.remove("oversized");
    }
  }
  resizeView(size) {
    const root = document.documentElement;
    const el = document.getElementById("mainview-container");
    if (size === "max") {
      root.style.setProperty(
        "--view-width",
        `calc(100% - var(--view-offset-left) - var(--view-offset-right))`,
      );
      root.style.setProperty(
        "--view-height",
        `calc(100% - var(--view-offset-top) - var(--view-offset-bottom))`,
      );
      el.style.marginLeft = "";

      this.isMaximized = true;
      this.currentSize = new Size(
        Math.floor(window.innerWidth),
        Math.floor(window.innerHeight),
      );
    } else {
      root.style.setProperty("--view-width", `${size.width}px`);
      root.style.setProperty("--view-height", `${size.height}px`);
      el.style.margin = "auto";
      this.isMaximized = false;
      this.currentSize = size;
    }
    this.handleShadow();

    this.viewSize = this.getViewSize();
  }
  handleShadow() {
    if (this.hasDisplay() === true) {
      const mainView = document.getElementById("mainview-container");
      const viewerDiv = document.getElementById("guac-div-viewer");
      if (this.isMaximized) {
        if (viewerDiv !== null && mainView !== null) {
          viewerDiv.classList.add("dropshadow", "hoverborder");
          mainView.classList.remove("hoverborder");
        }
      } else {
        if (viewerDiv !== null && mainView !== null) {
          viewerDiv.classList.remove("dropshadow", "hoverborder");
          mainView.classList.add("hoverborder");
        }
      }
    }
  }
  hasDisplay() {
    if (
      typeof document.Bootstrap.viewerGuac !== "undefined" &&
      document.Bootstrap.viewerGuac !== null &&
      document.Bootstrap.viewerGuac.displayWrapper !== null
    ) {
      return true;
    }
    return false;
  }
  readCSSVariable(variableName) {
    const root = document.documentElement;
    const styles = getComputedStyle(root);
    return styles.getPropertyValue(variableName).trim();
  }
  setInfo(info) {
    // this.overlay.showOverlayByMode(
    //   info.instanceInfo.parsedMode,
    //   info.instanceInfo.parsedModeExtended,
    // );
    // console.log("SETINFO:" + JSON.stringify(info));
    if (info.instanceInfo.parsedModeExtended === "done") {
      this.topbar.setMessage("");
    } else {
      this.topbar.setMessage(info.instanceInfo.parsedModeExtended);
    }
    if (
      typeof info.instanceInfo.resolutions !== "undefined" &&
      info.instanceInfo.resolutions.length > 0
    ) {
      this.populateResolutions(info.instanceInfo.resolutions);
    }
    return this.sidebar.updateInfo(info, this.currentSize, this.maxSize);
  }
  showView(viewId) {
    const views = document.querySelectorAll(".view");
    views.forEach((view) => {
      view.style.display = "none";
    });
    document.getElementById(viewId).style.display = "flex";
  }

  showDebug() {
    this.overlay.hideOverlay();
    this.currentView = "debug";
    this.showView("debug-view");
  }

  showStatus() {
    this.overlay.hideOverlay();
    this.currentView = "status";
    this.showView("status-view");
  }

  showClient() {
    if (
      document.Bootstrap.instanceInfo !== null &&
      document.Bootstrap.instanceInfo.instanceInfo !== null
    ) {
      const info = document.Bootstrap.instanceInfo.instanceInfo;
      this.overlay.showOverlayByMode(info.parsedMode, info.parsedModeExtended);
    } else {
      this.overlay.showOverlay();
    }
    this.handleShadow();
    this.currentView = "client";
    this.showView("client-view");
  }

  isDebugVisible() {
    return document.getElementById("debug-view").style.display === "flex";
  }

  isStatusVisible() {
    return document.getElementById("status-view").style.display === "flex";
  }

  isClientVisible() {
    return document.getElementById("client-view").style.display === "flex";
  }

  populateResolutions(resolutions) {
    const select = document.getElementById("resolutionSelect");
    select.innerHTML = "";
    const defaultResolutionOption = null;
    resolutions.forEach((resolution) => {
      const option = document.createElement("option");
      option.value = resolution;
      option.textContent = resolution === "max" ? "Maximize" : resolution;
      if (resolution === "1280x800") {
        defaultResolutionOption;
      }
      select.appendChild(option);
    });
    this.resolutions = resolutions;
    // select.value = "1680x1050";
    this.handleResolutionChange();
  }
  poupulateContypes(contypes) {
    const select = document.getElementById("contypeSelect");
    select.innerHTML = "";
    const defaultContypeOption = null;
    contypes.forEach((contype) => {
      const option = document.createElement("option");
      option.value = contype;
      option.textContent = contype;
      select.appendChild(option);
    });
    this.contypes = contypes;
  }
  async setScreen(configInstance, retries) {
    const svc = new BackendService(configInstance.backendUrl, retries);
    try {
      const data = await svc.setScreenInfo(
        configInstance.instance,
        configInstance.token,
        configInstance.contype,
        configInstance.resolution,
        configInstance.resize,
        configInstance.scale,
      );
      return { success: true };
    } catch (error) {
      console.log("Set screen params unsuccessful");
    }
    return {
      success: false,
    };
  }
}

class StatusView {
  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.viewElement = null;
    this.logo = null;
    this.iconLeft = null;
    this.iconRight = null;
    this.title = null;
    this.message = null;
    this.hint = null;
    this.messageWrapper = null;
    this.spinner = null;
    this.spinnerwrap = null;
    this.isSpinnerVisible = false;
  }

  buildView() {
    this.isSpinnerVisible = false;

    this.createLogo();
    this.createIconLeft("fa-solid fa-user");
    this.createIconRight("fa-solid fa-user");
    this.createTitle();
    this.createMessage();
    this.createHint();
    this.createMessageWrapper();
    this.createSpinner();
    this.createStatus();

    this.messageWrapper.appendChild(this.iconLeft);
    this.messageWrapper.appendChild(this.message);
    this.messageWrapper.appendChild(this.iconRight);
    this.spinnerwrap.appendChild(this.spinner);
    this.status.appendChild(this.logo);
    this.status.appendChild(this.spinnerwrap);
    this.status.appendChild(this.title);
    this.status.appendChild(this.messageWrapper);
    this.status.appendChild(this.hint);
    this.viewElement.appendChild(this.status);
    this.container.appendChild(this.viewElement);

    this.updateSpinner(true);
    this.updateTexts("Initialize", "AA", "BB");
    this.updateIconsNone();
  }

  createStatus() {
    this.viewElement = document.createElement("div");
    this.viewElement.id = this.viewId;
    this.viewElement.className = "view";
    this.status = document.createElement("div");
    this.status.id = "status-inner";
    this.status.className = "status-inner";
  }

  createMessageWrapper() {
    this.messageWrapper = document.createElement("div");
    this.messageWrapper.className = "status-msgwrap";
    this.messageWrapper.id = "status-msgwrap";
  }

  createTitle() {
    this.title = document.createElement("div");
    this.title.className = "status-title";
    this.title.id = "status-title";
  }

  createMessage() {
    this.message = document.createElement("div");
    this.message.className = "status-label";
    this.message.id = "status-label";
  }

  createHint() {
    this.hint = document.createElement("div");
    this.hint.className = "status-hint";
    this.hint.id = "status-hint";
  }

  createSpinner() {
    this.spinner = document.createElement("div");
    this.spinner.className = "status-spinner";
    this.spinner.id = "status-spinner";
    this.spinner.style.display = "none";
    this.spinnerwrap = document.createElement("div");
    this.spinnerwrap.className = "status-spinnerwrap";
    this.spinnerwrap.id = "status-spinnerwrap";
    this.spinnerwrap.style.display = "block";
  }

  createLogo() {
    this.logo = document.createElement("i");
    this.logo.className = "status-logo";
    this.logo.id = "status-logo";
  }

  createIconLeft(clsname) {
    this.iconLeft = document.createElement("i");
    this.iconLeft.className = "status-icon " + clsname;
    this.iconLeft.id = "status-icon-left";
  }

  createIconRight(clsname) {
    this.iconRight = document.createElement("i");
    this.iconRight.className = "status-icon " + clsname;
    this.iconRight.id = "status-icon-right";
  }

  updateView(title, message, hint, icon, spinner) {
    this.updateTitle(title);
    this.updateMessage(message);
    this.updateHint(hint);
    this.updateIcons(icon);
    this.updateSpinner(spinner);
  }

  updateIconsWarn() {
    const iconcls = "fa-solid fa-exclamation-triangle";
    this.updateIcons(iconcls, "#ffc107");
  }

  updateIconsInfo() {
    const iconcls = "fa-solid fa-info-circle";
    this.updateIcons(iconcls, "#17a2b8");
  }

  updateIconsError() {
    const iconcls = "fa-solid fa-times-circle";
    this.updateIcons(iconcls, "#dc3545");
  }

  updateIconsSuccess() {
    const iconcls = "fa-solid fa-check-circle";
    this.updateIcons(iconcls, "#28a745");
  }

  updateIconsNone() {
    this.updateIcons("", "#000000");
  }

  updateIcons(clsname, color) {
    this.iconLeft.style.color = color;
    this.iconRight.style.color = color;
    this.iconLeft.className = "status-icon " + clsname;
    this.iconRight.className = "status-icon " + clsname;
  }

  updateTitle(title) {
    this.title.innerHTML = title;
  }

  updateMessage(msg) {
    this.message.innerHTML = msg;
  }

  updateHint(hint) {
    this.hint.innerHTML = hint;
  }

  updateTexts(title, msg, hint) {
    this.updateTitle(title);
    this.updateMessage(msg);
    this.updateHint(hint);
  }

  updateSpinner(visible) {
    if (visible === false) {
      this.spinner.style.display = "none";
    } else {
      this.spinner.style.display = "block";
    }
  }

  incrementHint(sign, termination) {
    let hint = this.hint.innerHTML;
    if (hint === termination) {
      hint = sign;
    } else {
      hint = hint + sign;
    }
    this.updateHint(hint);
  }

  setStatusInit() {
    this.updateTexts("Initialize", "Preparing components", "");
    this.updateIconsNone();
  }

  setStatusStart() {
    this.updateTexts("Start Viewer", "Starting viewer service", "");
    this.updateSpinner(true);
    this.updateIconsNone();
  }

  setStatusStop() {
    this.updateTexts("Stop Viewer", "Stopping viewer service", "");
    this.updateSpinner(false);
    this.updateIconsNone();
  }

  setStatusConnected() {
    this.updateTexts("Connected", "Viewer connected", "");
    this.updateSpinner(false);
    this.updateIconsSuccess();
  }

  setStatusDisconnected() {
    this.updateTexts("Disconnected", "Reconnect disabled", "");
    this.updateSpinner(false);
    this.updateIconsNone();
  }

  setStatusConnecting() {
    this.updateTexts("Connecting", "Connecting websocket", "");
    this.updateSpinner(true);
    this.updateIconsInfo();
  }

  setStatusReconnect(reconnects) {
    this.updateTexts("Reconnect", "Reconnecting websocket", "");
    this.updateSpinner(true);
    if (reconnects > 0) {
      this.updateHint(reconnects + " failed attempt(s)");
      this.updateIconsInfo();
    } else {
      this.updateIconsNone();
    }
  }

  setStatusDelayed(reconnects) {
    this.updateTexts("Reconnect", "Reconnecting after disconnect");
    const hint = "Delaying reconnects! " + reconnects + " failed attempts";
    this.updateSpinner(true);
    this.updateHint(hint);
    this.updateIconsWarn();
    // console.error("Disconnected with " + reconnects + " failed attempts");
  }

  setStatusWait() {
    this.updateTexts("Waiting for Boot", "Testing connectivity", ".");
    this.updateSpinner(true);
    this.updateIconsNone();
  }

  setStatusPrepare() {
    this.updateTexts("Prepare Viewer", "Instance is online", "");
    this.updateSpinner(true);
    this.updateIconsNone();
  }

  setStatusFetch() {
    this.updateTexts("Prepare viewer", "Fetching resolutions", ".");
    this.updateSpinner(true);
    this.updateIconsNone();
  }

  setStatusResolution() {
    this.updateTexts("Switch resolution", "Changing display settings", "");
    this.updateSpinner(true);
    this.updateIconsInfo();
  }

  setStatusSwitch() {
    this.updateTexts("Switch Protocol", "Changing protocols", "");
    this.updateSpinner(true);
    this.updateIconsInfo();
  }
}

class ClientView {
  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.viewElement = null;
  }

  buildView() {
    this.viewElement = document.createElement("div");
    this.viewElement.id = this.viewId;
    this.viewElement.className = "view";
    this.container.appendChild(this.viewElement);
  }
}

class DebugView {
  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.viewElement = null;
  }

  buildView() {
    this.viewElement = document.createElement("div");
    this.viewElement.id = this.viewId;
    this.viewElement.className = "view";
    this.upper = document.createElement("div");
    this.upper.id = "debug-upper-div";
    this.upperRight = document.createElement("div");
    this.upperRight.id = "debug-upper-right";
    this.upperLeft = document.createElement("div");
    this.upperLeft.id = "debug-upper-left";
    this.lower = document.createElement("div");
    this.lower.id = "debug-lower-div";
    this.logdiv = document.createElement("div");
    this.logdiv.id = "logdiv";
    this.buttondiv = document.createElement("div");
    this.buttondiv.id = "debug-buttons";
    this.buttonClearLog = document.createElement("button");
    this.buttonClearLog.id = "debug-buttons-clearlog";
    this.buttonClearLog.textContent = "Clear Log";
    this.buttonClearLog.addEventListener("click", this.clearLog.bind(this));
    this.buttonClearPrintlist = document.createElement("button");
    this.buttonClearPrintlist.id = "debug-buttons-clearprint";
    this.buttonClearPrintlist.textContent = "Clear printed files";
    this.buttonClearPrintlist.addEventListener(
      "click",
      this.clearPrintlist.bind(this),
    );
    this.printdiv = document.createElement("div");
    this.printdiv.id = "printer-files";
    this.printhead = document.createElement("h3");
    this.printhead.id = "printer-files-head";
    this.printhead.textContent = "Printed files";
    this.printlistdiv = document.createElement("div");
    this.printlistdiv.id = "printer-files-listdiv";
    this.printdiv.appendChild(this.printhead);
    this.printdiv.appendChild(this.printlistdiv);
    this.upperRight.appendChild(this.printdiv);
    this.buttondiv.appendChild(this.buttonClearLog);
    this.buttondiv.appendChild(this.buttonClearPrintlist);
    this.upperLeft.appendChild(this.buttondiv);
    this.lower.appendChild(this.logdiv);
    this.upper.appendChild(this.upperLeft);
    this.upper.appendChild(this.upperRight);
    this.viewElement.appendChild(this.upper);
    this.viewElement.appendChild(this.lower);
    this.container.appendChild(this.viewElement);
  }

  clearLog() {
    this.logdiv.innerHTML = "";
  }
  clearPrintlist() {
    this.printlistdiv.innerHTML = "";
  }
  addLogElement(msg) {
    var clsName = "log-listelement";
    const childDivs = this.logdiv.querySelectorAll("div");
    const divCount = childDivs.length;
    if (divCount % 2 !== 0) {
      clsName = "log-listelement-odd";
    }
    const newElement = document.createElement("div");
    newElement.className = clsName;
    newElement.textContent = msg;
    this.logdiv.appendChild(newElement);
  }
  addPrintFile(f, link, name) {
    var clsName = "print-listelement";
    const childDivs = this.logdiv.querySelectorAll("div");
    const divCount = childDivs.length;
    if (divCount % 2 !== 0) {
      clsName = "print-listelement-odd";
    }
    const newElement = document.createElement("div");
    newElement.className = clsName;
    newElement.appendChild(link);
    this.printlistdiv.appendChild(newElement);
    const topbarCont = document.getElementById("topbar-container");
    const topbarButton = document.getElementById("btnDebug");
    if (
      typeof topbarCont !== "undefined" &&
      typeof topbarButton !== "undefined"
    ) {
      document.ViewerLayout.topbar.setMessage("File printed");
      topbarCont.classList.add("topbar-hover");
      topbarButton.classList.add("topbar-blink");
      setTimeout(() => {
        document.ViewerLayout.topbar.setMessage("");
        topbarCont.classList.remove("topbar-hover");
        topbarButton.classList.remove("topbar-blink");
      }, 3000);
    }
  }
}
class Overlay {
  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.viewElement = null;
    this.overlayBorder = null;
    this.overlayText = null;
    this.buttonHide = null;
    this.overlayHint = null;
    this.disabled = false;
    this.forced = false;
  }

  buildView() {
    this.overlayBorder = document.createElement("div");
    this.overlayBorder.id = "overlayBorder";

    this.overlayText = document.createElement("label");
    this.overlayText.textContent =
      "The viewer is disabled during object processing!\r\n\r\n" +
      "The Overlay will disappear automatically as soon as the app is running!\r\n\r\n" +
      "Disable only if you know what you do!\r\n\r\n";
    this.overlayText.id = "overlayText";
    this.overlayText.class = "overlay-text";
    this.overlayHint = document.createElement("label");
    this.overlayHint.textContent = "";
    this.overlayHint.id = "overlayHint";
    this.overlayHint.class = "overlay-hint";
    this.buttonHide = document.createElement("button");
    this.buttonHide.class = "";
    this.buttonHide.id = "btnHideOverlay";
    this.buttonHide.textContent = "Hide Overlay";
    this.buttonHide.addEventListener(
      "click",
      this.hideOverlayManual.bind(this),
    );
    this.overlayBorder.appendChild(this.overlayText);
    this.overlayBorder.appendChild(this.overlayHint);
    this.overlayBorder.appendChild(this.buttonHide);
    this.container.appendChild(this.overlayBorder);
    this.container.style.display = "none";
    this.container.style.pointerEvents = "none";
  }
  setOverlayTexts(newText, newHint) {
    this.setOverlayText(newText);
    this.setOverlayHint(newHint);
  }
  setOverlayText(newText) {
    this.overlayText.textContent = newText;
  }
  setOverlayHint(newHint) {
    this.overlayHint.textContent = newHint;
  }
  showOverlayByMode(mode, submode) {
    if (this.forced === true) {
      this.showOverlay();
    } else {
      if (
        document.ViewerLayout.currentView === "client" &&
        this.disabled === false
      ) {
        if (mode === "run-debug") {
          this.hideOverlay();
        } else if (mode === "run-app") {
          if (submode === "done") {
            this.hideOverlay();
          } else {
            this.showOverlay();
          }
        } else {
          this.showOverlay();
        }
      } else {
        this.hideOverlay();
      }
    }
  }
  showOverlay() {
    this.container.style.display = "flex";
    this.container.style.pointerEvents = "auto";
  }
  hideOverlay() {
    this.container.style.display = "none";
    this.container.style.pointerEvents = "none";
  }
  hideOverlayManual() {
    this.disabled = true;
    this.container.style.display = "none";
    this.container.style.pointerEvents = "none";
  }
}
class Topbar {
  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.divButtons = null;
    this.btnStatus = null;
    this.btnClient = null;
    this.btnDebug = null;
    this.labHover = null;
  }

  buildView() {
    this.divButtons = document.createElement("div");
    this.divButtons.id = "topbar-buttons";
    this.divButtons.class = "topbar-buttons";

    this.btnStatus = document.createElement("button");
    this.btnStatus.id = "btnStatus";
    this.btnStatus.textContent = "Status";
    this.btnStatus.addEventListener("click", () => {
      document.ViewerLayout.showStatus();
    });
    this.btnClient = document.createElement("button");
    this.btnClient.id = "btnClient";
    this.btnClient.textContent = "Client";
    this.btnClient.addEventListener("click", () => {
      document.ViewerLayout.showClient();
    });
    this.btnDebug = document.createElement("button");
    this.btnDebug.id = "btnDebug";
    this.btnDebug.textContent = "Printer";
    this.btnDebug.addEventListener("click", () => {
      document.ViewerLayout.showDebug();
    });
    this.labHover = document.createElement("label");
    this.labHover.id = "topbar-label";
    this.labHover.textContent = "";
    this.divButtons.appendChild(this.btnStatus);
    this.divButtons.appendChild(this.btnClient);
    this.divButtons.appendChild(this.btnDebug);
    this.container.appendChild(this.divButtons);
    this.container.appendChild(this.labHover);
  }
  setMessage(msg) {
    if (this.labHover !== null) {
      this.labHover.textContent = msg;
    }
  }
}

class ObjectInfo {
  viewId = null;
  containerId = null;
  container = null;
  name = null;
  env = null;
  app = null;
  nameDiv = null;

  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.name = null;
    this.env = null;
    this.app = null;
    this.stats = null;
    this.nameDiv = null;
  }
  buildView() {
    this.nameDiv = document.createElement("div");
    this.nameDiv.id = "instance-namediv";
    this.nameDiv.title = "Object Names";
    this.name = document.createElement("label");
    this.name.id = "instance-name";
    this.name.title = "Object Name";
    this.env = document.createElement("label");
    this.env.id = "instance-env";
    this.env.title = "Object Environment";
    this.app = document.createElement("label");
    this.app.id = "instance-app";
    this.app.title = "Object App";
    this.nameDiv.appendChild(this.name);
    this.nameDiv.appendChild(this.env);
    this.nameDiv.appendChild(this.app);
    this.container.appendChild(this.nameDiv);
  }
  setNames(name, env, app) {
    if (typeof this.name !== "undefined") {
      this.name.innerHTML = name;
    }
    if (typeof this.env !== "undefined") {
      this.env.innerHTML = env;
    }
    if (typeof this.app !== "undefined") {
      this.app.innerHTML = app;
    }
  }
}
class StatsInfo {
  viewId = null;
  containerId = null;
  container = null;
  name = null;
  env = null;
  app = null;
  nameDiv = null;

  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.stats = null;
    this.nameDiv = null;
  }
  buildView() {
    this.nameDiv = document.createElement("div");
    this.nameDiv.id = "instance-namediv";
    this.nameDiv.title = "Object Names";
    this.opcodes = document.createElement("label");
    this.opcodes.id = "instance-opcodes";
    this.opcodes.title = "Total opcodes received";
    this.ops = document.createElement("label");
    this.ops.id = "instance-ops";
    this.ops.title = "Opcodes per second";
    this.blobs = document.createElement("label");
    this.blobs.id = "instance-blobs";
    this.blobs.title = "Total blobs received";
    this.bps = document.createElement("label");
    this.bps.id = "instance-bps";
    this.bps.title = "Blobs per second";
    this.bbps = document.createElement("label");
    this.bbps.id = "instance-bbps";
    this.bbps.title = "Blobs per second";
    this.blobsize = document.createElement("label");
    this.blobsize.id = "instance-blobsize";
    this.blobsize.title = "Blob bytes received";
    this.nameDiv.appendChild(this.opcodes);
    this.nameDiv.appendChild(this.ops);
    this.nameDiv.appendChild(this.blobs);
    this.nameDiv.appendChild(this.bps);
    this.nameDiv.appendChild(this.blobsize);
    this.nameDiv.appendChild(this.bbps);
    this.container.appendChild(this.nameDiv);
  }
  setStats(stats) {
    if (typeof stats !== "undefined") {
      if (typeof stats.total_blobs !== "undefined") {
        this.opcodes.innerHTML = stats.total_blobs + " opcodes";
        this.ops.innerHTML = stats.opcodes_per_second.toFixed(2) + " O/s";
        this.blobs.innerHTML = stats.total_blobs + " blobs";
        this.bps.innerHTML = stats.blobs_per_second.toFixed(2) + " B/s";
        this.bbps.innerHTML =
          (stats.blobbytes_per_second / 1024).toFixed(2) + " KB/s";
        this.blobsize.innerHTML =
          (stats.size_blobs / 1024 / 1024).toFixed(2) + " MB";
      }
    }
  }
}
class ConnectionInfo {
  viewId = null;
  containerId = null;
  container = null;
  stateAvailable = null;
  stateSettings = null;
  stateViewtype = null;
  stateAvailable = null;
  modeDiv = null;

  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.resolutionSelect = null;
    this.stateAvailable = null;
    this.stateSettings = null;
    this.stateViewtype = null;
    this.stateConnected = null;
    this.modeDiv = null;
  }
  buildView() {
    this.stateDiv = document.createElement("div");
    this.stateDiv.id = "instance-state";
    this.stateAvailable = document.createElement("div");
    this.stateAvailable.id = "instance-available";
    this.stateAvailable.title = "Object Availability";
    this.stateSettings = document.createElement("div");
    this.stateSettings.id = "instance-settings";
    this.stateSettings.title = "Settings fetched";
    this.stateViewtype = document.createElement("div");
    this.stateViewtype.id = "instance-viewtype";
    this.stateViewtype.title = "Type of connection (App or Debug)";
    this.stateConnected = document.createElement("div");
    this.stateConnected.id = "instance-connected";
    this.stateConnected.title = "Websocket connection";
    this.modeDiv = document.createElement("div");
    this.modeDiv.id = "instance-mode";
    this.modeDiv.title = "Mode of execution";
    this.stateDiv.appendChild(this.stateAvailable);
    this.stateDiv.appendChild(this.stateSettings);
    this.stateDiv.appendChild(this.stateViewtype);
    this.stateDiv.appendChild(this.stateConnected);
    this.container.appendChild(this.stateDiv);
    this.container.appendChild(this.modeDiv);
  }
  setStates(colorAvailable, colorSettings, colorViewtype, colorConnected) {
    if (this.stateAvailable !== null) {
      this.stateAvailable.style.background = colorAvailable;
    }
    if (this.stateSettings !== null) {
      this.stateSettings.style.background = colorSettings;
    }
    if (this.stateViewtype !== null) {
      this.stateViewtype.style.background = colorViewtype;
    }
    if (this.stateConnected !== null) {
      this.stateConnected.style.background = colorConnected;
    }
  }
  setModes(mode, modeExt) {
    var msg = "";
    if (modeExt === "done") {
      modeExt = "Running";
    }
    if (mode === "run-clone") {
      msg = "(CLONE) " + modeExt;
    } else if (mode === "run-install") {
      msg = "(INSTALL) " + modeExt;
    } else if (mode === "run-debug") {
      msg = "(DEBUG) " + modeExt;
    } else if (mode === "run-app") {
      msg = "(APP) " + modeExt;
    } else {
      msg = "(UNKNOWN) " + modeExt;
    }
    if (this.modeDiv !== null) {
      this.modeDiv.innerHTML = "";
      this.modeDiv.appendChild(document.createTextNode(msg));
    }
  }
}

class ResolutionInfo {
  viewId = null;
  containerId = null;
  container = null;
  contypeSelect = null;
  resolutionSelect = null;
  resolutionResize = null;
  resolutionScale = null;
  resCurrent = null;
  isRecording = null;

  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.resolutionDiv = null;
    this.contypeSelect = null;
    this.resolutionSelect = null;
    this.resolutionResize = null;
    this.resolutionScale = null;
    this.btnReconnect = null;
    this.resCurrent = null;
    this.isRecording = false;
  }
  async buildView() {
    this.resolutionDiv = document.createElement("div");
    this.resolutionDiv.id = "instance-resolution";
    this.btnStart = document.createElement("button");
    this.btnStart.id = "instance-connect";
    this.btnStart.textContent = "Connect";
    this.btnStart.addEventListener("click", () => {
      document.Bootstrap.reconnect = true;
    });
    this.btnStop = document.createElement("button");
    this.btnStop.id = "instance-stop";
    this.btnStop.textContent = "Disconnect";
    this.btnStop.addEventListener("click", () => {
      document.Bootstrap.reconnect = false;
      document.Bootstrap.viewerGuac.disconnect();
      document.ViewerLayout.statusView.setStatusDisconnected();
    });
    this.btnReconnect = document.createElement("button");
    this.btnReconnect.id = "instance-reconnect";
    this.btnReconnect.textContent = "Reconnect";
    this.btnReconnect.addEventListener("click", () => {
      document.Bootstrap.reconnect = true;
      // if (
      //   document.Bootstrap.isConnected == true ||
      //   document.Bootstrap.isConnecting === true
      // ) {
      document.Bootstrap.viewerGuac.disconnect();
      // }
    });
    this.btnRecord = document.createElement("button");
    this.btnRecord.id = "instance-record";
    this.btnRecord.textContent = "Record";
    this.btnRecord.addEventListener("click", async () => {
      const guac = document.Bootstrap.viewerGuac;
      const ext = guac.extensions;
      this.isRecording = ext.isConnectedRecorder();
      if (ext.contype !== "rdp") {
        if (this.isRecording === true) {
          guac.stop_recording();
          this.isRecording = false;
          this.btnRecord.textContent = "Record";
        } else {
          this.isRecording = await guac.start_recording();
          if (this.isRecording === true) {
            this.btnRecord.textContent = "Stop recording";
          }
        }
      }
    });
    this.contypeSelect = document.createElement("select");
    this.contypeSelect.id = "contypeSelect";
    this.contypeSelect.addEventListener("change", () => {
      document.ViewerLayout.handleContypeChange(this.contypeSelect.value);
    });
    this.resolutionSelect = document.createElement("select");
    this.resolutionSelect.id = "resolutionSelect";
    this.resolutionSelect.addEventListener("change", () => {
      document.ViewerLayout.handleResolutionChange();
    });
    const opt = document.createElement("option");
    opt.value = "max";
    opt.textContent = "Max";
    this.resolutionSelect.appendChild(opt);
    this.resolutionMaxWrapper = document.createElement("div");
    this.resolutionMaxWrapper.className = "instance-wrapper";
    this.resolutionMaxWrapper.title = "Available window size";
    this.resMax = document.createElement("div");
    this.resMax.id = "instance-res-max";
    this.resMaxLabel = document.createElement("label");
    this.resMaxLabel.className = "sidebar-label";
    this.resMaxLabel.textContent = "Max:";
    this.resolutionCurrentWrapper = document.createElement("div");
    this.resolutionCurrentWrapper.className = "instance-wrapper";
    this.resolutionCurrentWrapper.title = "Currently chosen size";
    this.resCurrent = document.createElement("div");
    this.resCurrent.id = "instance-res-current";
    this.resCurrentLabel = document.createElement("label");
    this.resCurrentLabel.className = "sidebar-label";
    this.resCurrentLabel.textContent = "Current:";
    this.resolutionClientWrapper = document.createElement("div");
    this.resolutionClientWrapper.className = "instance-wrapper";
    this.resolutionClientWrapper.title = "Native display size";
    this.resolutionSelect.appendChild(opt);
    this.resClient = document.createElement("div");
    this.resClient.id = "instance-res-max";
    this.resClientLabel = document.createElement("label");
    this.resClientLabel.className = "sidebar-label";
    this.resClientLabel.textContent = "Client:";
    this.resolutionResizeWrapper = document.createElement("div");
    this.resolutionResizeWrapper.className = "checkbox-wrap";
    this.resolutionResizeWrapper.title = "Resize instance resolution";
    this.resolutionResize = document.createElement("input");
    this.resolutionResize.id = "resolutionResize";
    this.resolutionResize.Name = "resize";
    this.resolutionResize.type = "checkbox";
    this.resolutionResize.checked = true;
    this.resolutionResize.addEventListener("click", () => {
      document.ViewerLayout.handleResizeChange();
    });
    this.resolutionResizeLabel = document.createElement("label");
    this.resolutionResizeLabel.htmlFor = "resolutionResize";
    this.resolutionResizeLabel.appendChild(document.createTextNode("Resize"));
    this.resolutionScaleWrapper = document.createElement("div");
    this.resolutionScaleWrapper.className = "checkbox-wrap";
    this.resolutionScaleWrapper.title = "Scale to available size";
    this.resolutionScale = document.createElement("input");
    this.resolutionScale.id = "resolutionScale";
    this.resolutionScale.Name = "scale";
    this.resolutionScale.type = "checkbox";
    this.resolutionScale.checked = true;
    this.resolutionScale.addEventListener("click", () => {
      document.ViewerLayout.handleScaleChange();
    });
    this.resolutionScaleLabel = document.createElement("label");
    this.resolutionScaleLabel.htmlFor = "resolutionScale";
    this.resolutionScaleLabel.appendChild(document.createTextNode("Scale"));
    this.resolutionDiv.appendChild(this.btnReconnect);
    this.resolutionDiv.appendChild(this.btnStart);
    this.resolutionDiv.appendChild(this.btnStop);
    this.resolutionDiv.appendChild(this.btnRecord);
    this.resolutionResizeWrapper.appendChild(this.resolutionResize);
    this.resolutionResizeWrapper.appendChild(this.resolutionResizeLabel);
    this.resolutionScaleWrapper.appendChild(this.resolutionScale);
    this.resolutionScaleWrapper.appendChild(this.resolutionScaleLabel);
    this.resolutionMaxWrapper.appendChild(this.resMaxLabel);
    this.resolutionMaxWrapper.appendChild(this.resMax);
    this.resolutionCurrentWrapper.appendChild(this.resCurrentLabel);
    this.resolutionCurrentWrapper.appendChild(this.resCurrent);
    this.resolutionClientWrapper.appendChild(this.resClientLabel);
    this.resolutionClientWrapper.appendChild(this.resClient);
    this.resolutionDiv.appendChild(this.contypeSelect);
    this.resolutionDiv.appendChild(this.resolutionSelect);
    this.resolutionDiv.appendChild(this.resolutionResizeWrapper);
    this.resolutionDiv.appendChild(this.resolutionScaleWrapper);
    this.resolutionDiv.appendChild(this.resolutionMaxWrapper);
    this.resolutionDiv.appendChild(this.resolutionCurrentWrapper);
    this.resolutionDiv.appendChild(this.resolutionClientWrapper);
    this.container.appendChild(this.resolutionDiv);
  }
  setObjectContypes(contypes) {
    for (const contype of contypes) {
      console.log(contype);
    }
  }
  setResolutions(resCur, resMax, resClient) {
    this.setMaxResolution(resMax);
    this.setCurrentResolution(resCur);
    this.setClientResolution(resClient);
  }
  setCurrentResolution(resolution) {
    if (this.resCurrent !== null) {
      if (resolution === "max") {
        this.resCurrent.innerHTML = resolution;
      } else {
        this.resCurrent.innerHTML = resolution.toString();
      }
    }
  }
  setMaxResolution(resolution) {
    if (typeof this.resMax !== "undefined") {
      this.resMax.innerHTML = resolution.toString();
    }
  }
  setClientResolution(resolution) {
    if (typeof this.resClient !== "undefined") {
      this.resClient.innerHTML = resolution.toString();
    }
  }
}

class Sidebar {
  viewId = null;
  containerId = null;
  container = null;
  conInfo = null;
  resInfo = null;
  objInfo = null;
  statsInfo = null;
  constructor(viewId, containerId) {
    this.viewId = viewId;
    this.containerId = containerId;
    this.container = document.getElementById(this.containerId);
    this.objInfo = new ObjectInfo("object-info", this.container.id);
    this.statsInfo = new StatsInfo("stats-info", this.container.id);
    this.resInfo = new ResolutionInfo("resolution-info", this.container.id);
    this.conInfo = new ConnectionInfo("connection-info", this.container.id);
  }

  async buildView() {
    await this.resInfo.buildView();
    this.objInfo.buildView();
    this.statsInfo.buildView();
    this.conInfo.buildView();
  }
  updateInfo(info, resolutionCurrent, resolutionMax) {
    const infoInstance = info.instanceInfo;
    const infoPing = info.pingInfo;
    // console.log("INFO: " + JSON.stringify(infoInstance));
    this.objInfo.setNames(infoInstance.obj, infoInstance.env, infoInstance.app);
    this.statsInfo.setStats(infoInstance.stats);
    if (infoInstance !== "undefined" && infoInstance !== null) {
      const colorAvailable = "green";
      var colorSettings = "red";
      if (
        infoPing.available === true &&
        infoPing.connection === true &&
        infoInstance.resolutions.length > 0
      ) {
        colorSettings = "green";
      } else if (infoPing.available === true && infoPing.connection === true) {
        colorSettings = "orange";
      } else {
        colorSettings = "red";
      }
      var colorViewtype = "red";
      var colorConnected = "red";
      if (document.Bootstrap.viewerGuac.isConnecting) {
        colorConnected = "orange";
      } else if (document.Bootstrap.viewerGuac.isConnected) {
        colorConnected = "green";
      }
      if (
        infoInstance.parsedMode === "run-clone" ||
        infoInstance.parsedMode === "run-install" ||
        infoInstance.parsedMode === "run-debug"
      ) {
        colorViewtype = "orange";
      } else if (infoInstance.parsedMode === "run-app") {
        colorViewtype = "green";
      } else {
        colorViewtype = "red";
      }
      var displaySize = new Size(0, 0);
      if (
        document.Bootstrap.viewerGuac.displayWrapper !== null &&
        document.Bootstrap.viewerGuac.displayWrapper.isInitialized === true
      ) {
        displaySize =
          document.Bootstrap.viewerGuac.displayWrapper.currentDisplaySize;
      }
      this.conInfo.setModes(
        infoInstance.parsedMode,
        infoInstance.parsedModeExtended,
      );
      this.conInfo.setStates(
        colorAvailable,
        colorSettings,
        colorViewtype,
        colorConnected,
      );
      this.resInfo.setResolutions(
        resolutionCurrent,
        resolutionMax,
        displaySize,
      );
    } else {
      this.conInfo.setModes("none", "none");
      this.conInfo.setStates("red", "red", "red", "red");
      this.resInfosetResolutions(resolutionCurrent, resolutionMax);
    }
  }
}
