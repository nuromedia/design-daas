const DISPLAY_STATUS = "flex";
const DISPLAY_CLIENT = "flex";
const DISPLAY_DEBUG = "block";
//--
const ICON_FAMILY = "fa-solid";
const ICON_SUCCESS = "fa-circle-check";
const ICON_ERROR = "fa-circle-xmark";
const ICON_WARN = "fa-triangle-exclamation";
const ICON_INFO = "fa-circle-exclamation";
const COLOR_SUCCESS = "#00ff00";
const COLOR_ERROR = "#ff0000";
const COLOR_INFO = "#0000ff";
const COLOR_WARN = "#eeee00";
const COLOR_DEFAULT = "#000000";
const DEFAULT_SIZE = new Size(1280, 800);

class ViewDebug {
  divName = null;
  divObject = null;
  wrapper = null;
  dummy = null;
  constructor(container) {
    this.divName = container;
    this.divObject = document.getElementById(this.divName);
  }
  buildView() {
    this.createWrapper();
    this.createDummy();
    this.wrapper.appendChild(this.dummy);
    this.divObject.appendChild(this.wrapper);
  }
  createWrapper() {
    this.wrapper = document.createElement("div");
    this.wrapper.className = "debug-wrapper";
    this.wrapper.id = "debug-wrapper";
  }
  createDummy() {
    this.dummy = document.createElement("div");
    this.dummy.className = "debug-dummy";
    this.dummy.id = "debug-dummy";
    this.dummy.innerHTML = "BBB";
  }
}
class ViewClient {
  divName = null;
  divObject = null;
  wrapper = null;
  dummy = null;
  constructor(container) {
    this.divName = container;
    this.divObject = document.getElementById(this.divName);
  }
  buildView() {
    this.createWrapper();
    this.createDummy();
    this.wrapper.appendChild(this.dummy);
    this.divObject.appendChild(this.wrapper);
  }
  createWrapper() {
    this.wrapper = document.createElement("div");
    this.wrapper.className = "client-wrapper";
    this.wrapper.id = "client-wrapper";
  }
  createDummy() {
    this.dummy = document.createElement("div");
    this.dummy.className = "client-dummy";
    this.dummy.id = "client-dummy";
    this.dummy.innerHTML = "AAA";
  }
}
class ViewStatus {
  divName = null;
  divObject = null;
  logo = null;
  iconLeft = null;
  iconRight = null;
  title = null;
  message = null;
  hint = null;
  wrapper = null;
  messageWrapper = null;
  spinner = null;
  spinnerwrap = null;
  isSpinnerVisible = false;
  constructor(container) {
    this.divName = container;
    this.divObject = document.getElementById(this.divName);
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
    this.wrapper.appendChild(this.status);
    this.divObject.appendChild(this.wrapper);

    this.updateSpinner(true);
    this.updateTexts("Initialize", "AA", "BB");
    this.updateIconsNone();
  }
  createStatus() {
    this.wrapper = document.createElement("div");
    this.wrapper.id = "status-outer";
    this.wrapper.className = "status-outer";
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
    this.iconLeft.id = "status-icon";
  }
  createIconRight(clsname) {
    this.iconRight = document.createElement("i");
    this.iconRight.className = "status-icon " + clsname;
    this.iconRight.id = "status-icon";
  }
  updateView(title, message, hint, icon, spinner) {
    this.updateTitle(title);
    this.updateMessage(message);
    this.updateHint(hint);
    this.updateIcons(icon);
    this.updateSpinner(spinner);
  }
  updateIconsWarn() {
    var iconcls = ICON_FAMILY + " " + ICON_WARN;
    this.updateIcons(iconcls, COLOR_WARN);
  }
  updateIconsInfo() {
    var iconcls = ICON_FAMILY + " " + ICON_INFO;
    this.updateIcons(iconcls, COLOR_INFO);
  }
  updateIconsError() {
    var iconcls = ICON_FAMILY + " " + ICON_ERROR;
    this.updateIcons(iconcls, COLOR_ERROR);
  }
  updateIconsSuccess() {
    var iconcls = ICON_FAMILY + " " + ICON_SUCCESS;
    this.updateIcons(iconcls, COLOR_SUCCESS);
  }
  updateIconsNone() {
    this.updateIcons("", COLOR_DEFAULT);
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
    var hint = this.hint.innerHTML;
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
  setStatusReconnect(error, reconnects) {
    this.updateTexts("Reconnect", "Reconnecting websocket", "");
    this.updateSpinner(true);
    if (reconnects > 1) {
      this.updateHint(reconnects + " failed attempt(s)");
      this.updateIconsInfo();
    } else {
      this.updateIconsNone();
    }
  }
  setStatusDelayed(error, reconnects) {
    this.updateTexts("Reconnect", "Reconnecting after error " + error.code);
    var hint = "Delaying reconnects! " + reconnects + " failed attempts";
    this.updateSpinner(true);
    this.updateHint(hint);
    this.updateIconsWarn();
    this.log_error(
      "Error " + error.code + " with " + reconnects + " failed  attempts",
    );
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

class ViewerLayout {
  cfg = null;
  objOuter = null;
  objInner = null;
  objDisplay = null;
  objSize = null;
  // objContainer = null;
  body = null;
  status = null;
  client = null;
  debug = null;
  isStatusVisible = false;
  isClientVisible = false;
  isDebugVisible = false;
  // --
  // viewSize = { width: 0, height: 0 };
  // scaleSize = { width: 0, height: 0 };
  // viewScale = 1;
  // isLogEnabled = false;
  // isSwitcherLogEnabled = false;
  // isViewerScaled = false;
  // isFixedSize = false;
  // isMaximized = true;

  constructor(cfg) {
    this.cfg = cfg;
    this.isLogEnabled = this.cfg.tconf.log_enabled === "1";
    this.isSwitcherLogEnabled = this.cfg.tconf.log_switcher === "1";
    this.body = document.body;
    // this.objInner = document.getElementById(this.cfg.divInner);
    this.buildView();
    this.showStatus();
    this.log("ViewerLayout initialized");
  }

  buildView() {
    this.isStatusVisible = false;
    this.isClientVisible = false;
    this.isDebugVisible = false;
    this.client = new ViewClient(this.cfg.divOuter);
    this.client.buildView();
    this.debug = new ViewDebug(this.cfg.divOuter);
    this.debug.buildView();
    this.status = new ViewStatus(this.cfg.divOuter);
    this.status.buildView();
  }
  showStatus() {
    this.status.wrapper.style.display = DISPLAY_STATUS;
    this.client.wrapper.style.display = "none";
    this.debug.wrapper.style.display = "none";
    this.isStatusVisible = true;
    this.isClientVisible = false;
    this.isDebugVisible = false;
  }
  showClient() {
    this.status.wrapper.style.display = "none";
    this.client.wrapper.style.display = DISPLAY_CLIENT;
    this.debug.wrapper.style.display = "none";
    this.isStatusVisible = false;
    this.isClientVisible = true;
    this.isDebugVisible = false;
  }
  showDebug() {
    this.status.wrapper.style.display = "none";
    this.client.wrapper.style.display = "none";
    this.debug.wrapper.style.display = DISPLAY_DEBUG;
    this.isStatusVisible = false;
    this.isClientVisible = true;
    this.isDebugVisible = false;
  }
  setScaledSize(newScale, size) {
    this.viewSize = size;
    this.viewScale = newScale;
    if (this.viewScale === 1) {
      this.isViewerScaled = false;
    } else {
      this.isViewerScaled = true;
    }
    this.scaleSize = new Size(
      this.viewSize.width * this.viewScale,
      this.viewSize.height * this.viewScale,
    );
    this.objSize.style.width = this.scaleSize.width + "px";
    this.objSize.style.height = this.scaleSize.height + "px";
    this.objSize.style.margin = "auto";
    this.isMaximized = false;
    this.isFixedSize = true;
  }
  setSize(size) {
    this.viewSize = size;
    this.objSize.style.width = this.scaleSize.width + "px";
    this.objSize.style.height = this.scaleSize.height + "px";
    this.objSize.style.margin = "auto";
    this.isMaximized = false;
    this.isFixedSize = true;
  }
  maximizeSize() {
    var width = parseFloat(document.body.clientWidth);
    var height = parseFloat(document.body.clientHeight);
    this.viewSize = new Size(Math.floor(width), Math.floor(height));
    this.scaleSize = new Size(Math.floor(width), Math.floor(height));
    this.objSize.style.width = "100%";
    this.objSize.style.height = "100%";
    this.objSize.style.margin = "0px";
    this.isMaximized = true;
    this.isFixedSize = false;
  }
  setWantedSize(options) {
    if (options !== null && options.wantsMaximize) {
      this.maximizeSize();
    } else {
      this.setScaledSize(1, options.wantedSize);
    }
  }
  log(msg) {
    if (this.isLogEnabled === true && this.isSwitcherLogEnabled === true) {
      console.log("SWITCH: " + msg);
    }
  }
  log_error(msg) {
    console.error("SWITCH: " + msg);
  }
}
