DEFAULT_DPI = 96;
DEFAULT_COLORS = 32;
DEFAULT_LOSSLESS = false;
DEFAULT_CONTYPE = "sysvnc";
class DaasConfigViewer {
  constructor(
    log_enabled,
    log_resize,
    log_summary,
    log_tunnel,
    log_client,
    log_switcher,
    log_watcher,
    observer_ms,
    fetch_ms,
    check_ms,
    reconnect_ms,
    default_reload_ms,
    delayed_reload_ms,
    reconnect_max,
    reconnect_enabled,
    resolution_check_init,
  ) {
    this.log_enabled = log_enabled;
    this.log_resize = log_resize;
    this.log_summary = log_summary;
    this.log_tunnel = log_tunnel;
    this.log_client = log_client;
    this.log_switcher = log_switcher;
    this.log_watcher = log_watcher;
    this.observer_ms = observer_ms;
    this.fetch_ms = fetch_ms;
    this.check_ms = check_ms;
    this.reconnect_min_ms = reconnect_ms;
    this.reconnect_default_ms = default_reload_ms;
    this.reconnect_delayed_ms = delayed_reload_ms;
    this.reconnect_max = reconnect_max;
    this.reconnect_enabled = reconnect_enabled;
    this.resolutioncheck_init = resolution_check_init;
  }
  str() {
    return JSON.stringify(this);
  }
}

class DaasConfigInst {
  tconf = null;
  guac = null;
  divOuter = null;
  divInner = null;
  backendUrl = null;
  tunnelUrl = null;
  instance = null;
  owner = null;
  token = null;
  referrer = null;
  contype = null;
  resolution = null;
  resize = null;
  scale = null;
  dpi = DEFAULT_DPI;
  colors = DEFAULT_COLORS;
  lossless = DEFAULT_LOSSLESS;
  isvm = null;
  iswin = null;

  constructor(
    tconf,
    Guacamole,
    outer,
    inner,
    backendUrl,
    tunnelUrl,
    inst,
    owner,
    token,
    ref,
    contype,
    resolution,
    resize,
    scale,
    dpi,
    lossless,
    colors,
    isvm,
    iswin,
  ) {
    this.tconf = tconf;
    this.guac = Guacamole;
    this.divOuter = outer;
    this.divInner = inner;
    this.backendUrl = backendUrl;
    this.tunnelUrl = tunnelUrl;
    this.instance = inst;
    this.owner = owner;
    this.token = token;
    this.referrer = ref;
    this.contype = contype;
    this.resolution = resolution;
    this.resize = resize;
    this.scale = scale;
    this.dpi = parseInt(dpi);
    this.colors = parseInt(colors);
    this.lossless = lossless === "1" ? true : false;
    this.isvm = isvm === "1" ? true : false;
    this.iswin = iswin === "1" ? true : false;
  }
  str() {
    return JSON.stringify(this);
  }
}
