// Jinja Template Input
var hostproto = "{{hostproto}}";
var hostip = "{{hostip}}";
var hostport = "{{hostport}}";

var isMaximized = true;

var rttResults = [];
var rttText = "foo";

// Listen for iframe reload event
window.addEventListener("message", (event) => {
  if (event.data.type === "DaaSCustomReloadEvent") {
    console.log("RELOAD: Received reload event: " + event.data.data);
  }
});

// function refocusGuacamole(displayElement) {
//   var focused = document.activeElement;
//   if (focused && focused !== document.body) return;
//
//   if (displayElement !== null) {
//     displayElement.focus();
//   }
// }
// document.addEventListener("click", refocusGuacamole);
// document.addEventListener("keydown", refocusGuacamole);

class Timespan {
  begin = 0;
  end = 0;
  diff = 0;

  constructor(begin, end) {
    this.begin = begin;
    this.end = end;
    this.diff = this.end - this.begin;
  }
  toString() {
    return this.diff.toString().padStart(4, " ") + "ms";
  }
  toJSON() {
    return {
      begin: this.begin,
      end: this.end,
      diff: this.diff,
    };
  }
}
class MeasuredTimings {
  rttRequest = new Timespan(0, 0);
  rttAuth = new Timespan(0, 0);
  rttTask = new Timespan(0, 0);
  owdClient2Backend = new Timespan(0, 0);
  owdBackend2Client = new Timespan(0, 0);
  owdBackend2Inst = new Timespan(0, 0);
  owdInst2Backend = new Timespan(0, 0);
  owdClient2Inst = new Timespan(0, 0);
  owdInst2Client = new Timespan(0, 0);
  totalDirections = 0;
  totalDelay = 0;
  totalOwd = 0;

  toJSON() {
    return {
      rttReq: this.rttRequest.toJSON(),
      rttAuth: this.rttAuth.toJSON(),
      rttTask: this.rttTask.toJSON(),
      owdClient2Backend: this.owdClient2Backend.toJSON(),
      owdBackend2Inst: this.owdBackend2Inst.toJSON(),
      owdClient2Inst: this.owdClient2Inst.toJSON(),
      owdBackend2Client: this.owdBackend2Client.toJSON(),
      owdInst2Backend: this.owdInst2Backend.toJSON(),
      owdInst2Client: this.owdInst2Client.toJSON(),
      totalDirections: this.totalDirections,
      totalDelay: this.totalDelay,
      totalOwd: this.totalOwd,
    };
  }
  constructor(measured, reqtime, rttdata) {
    // Calculate Timings
    this.rttRequest = reqtime;
    this.rttAuth = new Timespan(
      measured["internal_auth_requested_at"],
      measured["internal_auth_responded_at"],
    );
    this.rttTask = new Timespan(
      measured["internal_task_requested_at"],
      measured["internal_task_responded_at"],
    );
    this.owdClient2Backend = new Timespan(
      reqtime.begin,
      measured["external_request_received_at"],
    );
    this.owdBackend2Inst = new Timespan(
      measured["internal_task_requested_at"],
      rttdata.end,
    );
    this.owdInst2Backend = new Timespan(
      rttdata.end,
      measured["internal_task_responded_at"],
    );
    this.owdBackend2Client = new Timespan(
      measured["external_request_responded_at"],
      reqtime.end,
    );
    this.owdClient2Inst = new Timespan(reqtime.begin, rttdata.end);
    this.owdInst2Client = new Timespan(rttdata.end, reqtime.end);

    // Calculate sums
    this.totalDirections = this.owdClient2Inst.diff + this.owdInst2Client.diff;
    this.totalOwd =
      this.owdClient2Backend.diff +
      this.owdBackend2Inst.diff +
      this.owdInst2Backend.diff +
      this.owdBackend2Client.diff;
    this.totalDelay =
      this.totalDirections -
      this.rttTask.diff -
      this.rttAuth.diff -
      this.owdClient2Backend.diff -
      this.owdBackend2Client.diff;
  }

  get_info_owd() {
    return (
      "--- One-Way Delays (OWD) -----------------------------------------" +
      "\nClient  -> Backend  : " +
      this.owdClient2Backend.toString() +
      "\nBackend -> Inst     : " +
      this.owdBackend2Inst.toString() +
      "\nBackend <- Inst     : " +
      this.owdInst2Backend.toString() +
      "\nClient  <- Backend  : " +
      this.owdBackend2Client.toString() +
      "\nSum Individual OWD  = " +
      this.totalOwd.toString().padStart(4, " ") +
      "ms" +
      "\nInternal Processing : " +
      (this.totalDelay + this.rttAuth.diff).toString().padStart(4, " ") +
      "ms" +
      "\nTotal Request Time  = " +
      (this.totalOwd + this.rttAuth.diff + this.totalDelay)
        .toString()
        .padStart(4, " ") +
      "ms"
    );
  }
  get_info_dir() {
    return (
      "\n--- Full Directions ----------------------------------------------" +
      "\nClient -> Instance  : " +
      this.owdClient2Inst.toString() +
      "\nClient <- Instance  : " +
      this.owdInst2Client.toString() +
      "\nTotal               = " +
      this.totalDirections.toString().padStart(4, " ") +
      "ms"
    );
  }
  get_info_rtt() {
    return (
      "\n--- Roundtrip times (RTT) ----------------------------------------" +
      "\nAuth Request        : " +
      this.rttAuth.toString() +
      "\nTask Duration       : " +
      this.rttTask.toString() +
      "\nFull Client Request : " +
      this.rttRequest.toString()
    );
  }

  log_info() {
    console.log(this.get_info_rtt());
    console.log(this.get_info_dir());
    console.log(this.get_info_owd());
  }
}
class TimingParser {
  measured = null;
  rttdata = null;
  reqtime = null;
  timing = null;
  hasTiming = false;
  hasFormData = false;
  hasRttData = false;
  hasReqTime = false;

  constructor(data) {
    if (data !== null) {
      this.formdata = this.parseJsonFormdata(data);
      if (this.formdata !== null) {
        this.hasFormData = true;
        this.reqtime = this.getRequestDuration(data, this.formdata);
        if (this.reqtime !== null && this.reqtime.diff > 0) {
          this.hasReqTime = true;
          this.measured = this.parseJsonTimings(data);
          this.rttdata = this.splitRttResponse(data);
          if (this.rttdata !== null && this.rttdata.diff > 0) {
            this.hasRttData = true;
            this.timing = new MeasuredTimings(
              this.measured,
              this.reqtime,
              this.rttdata,
            );
            if (this.timing.totalDirections > 0) {
              rttResults.push(this.timing);
              this.hasTiming = true;
            }
          }
        }
      }
    }
  }
  printAvailableTiming() {
    if (this.hasTiming === true) {
      this.timing.log_info();
    } else if (this.hasReqTime) {
      console.log("RTT Request: " + this.reqtime.toString());
    }
  }
  splitRttResponse(data) {
    var result = null;
    if (typeof data["sys_log"] !== "undefined" && data["sys_log"] !== "") {
      if (data["sys_log"].startsWith("rtt")) {
        var timings = data["sys_log"].slice(4);
        var arr = timings.split(",");
        if (arr.length === 3) {
          var mapped = arr.map(Number);
          return new Timespan(mapped[0], mapped[1]);
        }
      }
    }
    return result;
  }
  getRequestDuration(data, formdata) {
    var result = null;
    if (
      formdata !== null &&
      data !== null &&
      typeof formdata["timestamp"] !== "undefined" &&
      typeof data["timestamp_received"] !== "undefined"
    ) {
      var ts_send = formdata["timestamp"];
      var ts_rec = data["timestamp_received"];
      if (typeof ts_send !== "undefined" && typeof ts_rec !== "undefined") {
        result = new Timespan(parseInt(ts_send), parseInt(ts_rec));
      }
    }
    return result;
  }
  parseJsonTimings(data) {
    var measured = null;
    if (typeof data["timings"] !== "undefined") {
      var timings = data["timings"];
      if (timings.includes("'") === true) {
        timings = timings.replace(/'/g, '"');
      }
      if (timings.includes(": None,") === true) {
        timings = timings.replace(/(?<=:\s*)None(?=[,}])/g, "null");
      }
      measured = JSON.parse(timings);
    }
    return measured;
  }

  parseJsonFormdata(data) {
    var result = null;
    if (
      typeof data["http_params_form"] !== "undefined" &&
      data["http_params_form"] !== ""
    ) {
      var response = data["http_params_form"];
      if (response.includes("'") === true) {
        response = response.replace(/'/g, '"');
      }
      if (response.includes(": None,") === true) {
        response = response.replace(/(?<=:\s*)None(?=[,}])/g, "null");
      }
      result = JSON.parse(response);
    }
    return result;
  }
}
async function getViewerTemplate(url) {
  var method = "GET";
  var formData = new FormData();
  const data = {};
  let token = localStorage.getItem("token");
  var headers = {
    Accept: "application/json",
    Authorization: "Bearer " + token,
  };
  data["timestamp"] = Date.now();
  formData.append("timestamp", data["timestamp"]);
  document.getElementById("request").value =
    method + " " + url + "\n" + JSON.stringify(data, null, 2);

  try {
    var options = { method: method };
    if (method == "POST") {
      options = { method: method, body: formData, headers: headers };
    } else if (method == "GET") {
      options = { method: method, headers: headers };
    }
    var ret = await fetch(url, options)
      .then(function (response) {
        return response.text();
      })
      .then(function (data) {
        return data;
      })
      .catch(function (err) {
        console.error("Failed to fetch viewer template");
        document.getElementById("response").value = "Error fetching data";
        console.log(JSON.stringify(err));
      });
    return ret;
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("response").value = "Error fetching data";
  }
}
async function submitForm(url, method, formid) {
  var form = document.getElementById(formid);
  var formData = new FormData(form);
  const data = {};
  let token = localStorage.getItem("token");
  var headers = {
    Accept: "application/json",
    Authorization: "Bearer " + token,
  };
  formData.forEach((value, key) => {
    data[key] = value;
  });
  data["timestamp"] = Date.now();
  formData.append("timestamp", data["timestamp"]);
  // Update the Request textarea
  document.getElementById("request").value =
    method + " " + url + "\n" + JSON.stringify(data, null, 2);

  // For GET request, add the data to the URL as query parameters
  if (method === "GET") {
    url += "?" + new URLSearchParams(data).toString();
  }
  try {
    // Get form data
    var options = { method: method };
    if (method == "POST") {
      options = { method: method, body: formData, headers: headers };
    }
    // Fetch the URL
    await fetch(url, options)
      .then(async function (response) {
        return response.json();
      })
      .then(async function (data) {
        var now = Date.now();
        data["timestamp_received"] = now;
        // checkTimings(data);
        document.getElementById("response").value = JSON.stringify(
          data,
          null,
          2,
        );
        if (data["id_instance"]) {
          this.read_instance_id(data);
        }
        if (data["response_url"]) {
          await this.read_viewer_url(data);
        }
      })
      .catch(function (err) {
        console.error("Failed to fetch data");
        document.getElementById("response").value = "Error fetching data";
        console.log(JSON.stringify(err));
      });
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("response").value = "Error fetching data";
  }
}

async function updateDashboard(url) {
  data = await get_dashboard_info(url);
  cons = data.response_data.dashboardinfo.available_connections;
  const conElement = document.getElementById("dashboard-connections");
  for (let i in cons) {
    console.log(JSON.stringify(cons[i]));
    const option = document.createElement("option");
    option.value = cons[i].id_inst;
    option.textContent = cons[i].id_inst;
    conElement.appendChild(option);
  }
}
async function get_dashboard_info(url) {
  var method = "POST";
  var formData = new FormData();
  const data = {};
  var result = null;
  let token = localStorage.getItem("token");
  var headers = {
    Accept: "application/json",
    Authorization: "Bearer " + token,
  };
  formData.forEach((value, key) => {
    data[key] = value;
  });
  data["timestamp"] = Date.now();
  formData.append("timestamp", data["timestamp"]);
  try {
    var options = { method: method, body: formData, headers: headers };
    await fetch(url, options)
      .then(async function (response) {
        return response.json();
      })
      .then(async function (data_out) {
        var now = Date.now();
        data_out["timestamp_received"] = now;
        result = data_out;
      })
      .catch(function (err) {
        console.error("Failed to fetch dashboard info");
        console.log(JSON.stringify(err));
      });
  } catch (error) {
    console.error("Error:", error);
  }
  return result;
}
async function read_viewer_url(data) {
  if (
    typeof data["response_url"] !== "undefined" &&
    data["response_url"] !== ""
  ) {
    var fullurl = data["response_url"];
    var viewer = document.getElementById("viewer");
    var stoptextvm = document.getElementById("vmstoptext");
    var stoptextobj = document.getElementById("objstoptext");
    var stoptextcont = document.getElementById("containerstoptext");
    stoptextobj.setAttribute("value", data["id_instance"]);
    stoptextvm.setAttribute("value", data["id_instance"]);
    stoptextcont.setAttribute("value", data["id_instance"]);
    if (data["response_url"] != "-") {
      document.getElementById("viewerurl").value = data["response_url"];
      // viewer.setAttribute("src", fullurl);
      const templateText = await getViewerTemplate(fullurl);
      const iframeDoc = viewer.contentWindow.document;
      iframeDoc.open();
      iframeDoc.write(templateText);
      iframeDoc.close();
    } else {
      document.getElementById("viewerurl").value = "";
      viewer.setAttribute("src", "");
    }
  }
}
function read_instance_id(data) {
  if (
    typeof data["id_instance"] !== "undefined" &&
    data["id_instance"] !== ""
  ) {
    var stoptextvm = document.getElementById("vmstoptext");
    var stoptextobj = document.getElementById("objstoptext");
    var stoptextcont = document.getElementById("containerstoptext");
    stoptextobj.setAttribute("value", data["id_instance"]);
    stoptextvm.setAttribute("value", data["id_instance"]);
    stoptextcont.setAttribute("value", data["id_instance"]);
  }
}
async function submitTiming(url, method, formid) {
  var form = document.getElementById(formid);
  var formData = new FormData(form);
  var data = {};
  formData.forEach((value, key) => {
    data[key] = value;
  });
  var elIter = document.getElementById("rttiter");
  var iterations = parseInt(data["iter"]);
  for (let index = 0; index < iterations; index++) {
    setTimeout(async function () {
      elIter.value = iterations - index;
      await submitForm(url, method, formid);
    }, 5000 * index);
  }
}
function checkTimings(data) {
  var parser = new TimingParser(data);
  parser.printAvailableTiming();
  if (rttResults.length > 0) {
    var nameElement = document.getElementById("downloadname");
    var container = document.getElementById("rttcontainer");
    var downloadButton = document.getElementById("rttdownload");
    if (typeof downloadButton !== "undefined" && downloadButton !== null) {
      container.removeChild(downloadButton);
    }

    var results = generateRttDownload();
    const blob = new Blob([results], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    var txt = "Download <br/>(" + rttResults.length + " Results)";
    downloadButton = document.createElement("button");
    downloadButton.id = "rttdownload";
    downloadButton.innerHTML = txt;
    downloadButton.addEventListener("click", function () {
      const link = document.createElement("a");
      link.href = url;
      link.download = nameElement.value;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    });
    container.appendChild(downloadButton);
  }
}

function generateRttDownload() {
  if (rttResults.length > 0) {
    var nameElement = document.getElementById("downloadname");
    var lines = [];
    var summary = {
      summary: true,
      name: nameElement.value,
      samples: rttResults.length,
      rttReq: 0,
      rttAuth: 0,
      rttTask: 0,
      owdClient2Backend: 0,
      owdBackend2Client: 0,
      owdBackend2Inst: 0,
      owdInst2Backend: 0,
      totalDirections: 0,
      totalDelay: 0,
      totalOwd: 0,
    };

    for (var i = 0; i < rttResults.length; i++) {
      var result = rttResults[i];
      summary.rttReq += result.rttRequest.diff;
      summary.rttAuth += result.rttAuth.diff;
      summary.rttTask += result.rttTask.diff;
      summary.owdClient2Backend += result.owdClient2Backend.diff;
      summary.owdBackend2Client += result.owdBackend2Client.diff;
      summary.owdBackend2Inst += result.owdBackend2Inst.diff;
      summary.owdInst2Backend += result.owdInst2Backend.diff;
      summary.totalDirections += result.totalDirections;
      summary.totalDelay += result.totalDelay;
      summary.totalOwd += result.totalOwd;
      lines.push(result.toJSON());
    }
    summary.rttReq /= rttResults.length;
    summary.rttAuth /= rttResults.length;
    summary.rttTask /= rttResults.length;
    summary.owdClient2Backend /= rttResults.length;
    summary.owdBackend2Client /= rttResults.length;
    summary.owdBackend2Inst /= rttResults.length;
    summary.owdInst2Backend /= rttResults.length;
    summary.totalDirections /= rttResults.length;
    summary.totalDelay /= rttResults.length;
    summary.totalOwd /= rttResults.length;
    lines.push(summary);
    rttText = JSON.stringify(lines);
  }
  return rttText;
}
function updateViewer() {
  var viewer = document.getElementById("viewer");
  var txturl = document.getElementById("viewerurl");
  viewer.setAttribute("src", txturl.value);
  maximizeViewer();
}

function maximizeViewer() {
  var viewer = document.getElementById("viewer");
  if (viewer !== null) {
    viewer.style.width = "100%";
    viewer.style.height = "100%";
    isMaximized = true;
  }
}
function resizeViewer(width, height) {
  var viewer = document.getElementById("viewer");
  if (viewer !== null) {
    viewer.style.width = width + "px";
    viewer.style.height = height + "px";
    isMaximized = false;
  }
}
function setViewerInstance() {
  var txturl = document.getElementById("viewerurl");
  var stoptextvm = document.getElementById("vmstoptext");
  var stoptextphase = document.getElementById("objstoptext");
  var stoptextcont = document.getElementById("containerstoptext");

  var insts = document.getElementById("dashboard-connections");
  var selectedValue = insts.value;

  stoptextvm.setAttribute("value", selectedValue);
  stoptextphase.setAttribute("value", selectedValue);
  stoptextcont.setAttribute("value", selectedValue);
  txturl.value =
    hostproto +
    "://" +
    hostip +
    ":" +
    hostport +
    "/viewer/template/" +
    selectedValue;
  viewer.setAttribute("src", txturl.value);
  updateViewer();
}
async function runEnvironment(id, name) {
  var txtid = document.getElementById("envrun-id");
  var txtname = document.getElementById("envrun-name");
  txtid.setAttribute("value", id);
  txtname.setAttribute("value", name);
  await submitForm(
    hostproto + "://" + hostip + ":" + hostport + "/phases/environment_run",
    "POST",
    "phases-environment-run",
  );
}
async function create_from_app(id, name) {
  var txtid = document.getElementById("envrun-id");
  var txtname = document.getElementById("envrun-name");
  txtid.setAttribute("value", id);
  txtname.setAttribute("value", name);
  await submitForm(
    hostproto + "://" + hostip + ":" + hostport + "/phases/environment_run",
    "POST",
    "phases-environment-run",
  );
}

function clearViewer() {
  document.getElementById("viewerurl").value = "";
  var viewer = document.getElementById("viewer");
  viewer.setAttribute("src", "");
}
function fullscreenViewer() {
  var url = document.getElementById("viewerurl").value;
  window.open(url, "_blank").focus();
}

function printViewerSize() {
  var viewer = document.getElementById("viewer");
  console.log(viewer.offsetWidth + "x" + viewer.offsetHeight);
}

function toggleNav() {
  var nav = document.getElementById("navcolumn");
  // if (nav.style.display != "flex") {
  //   nav.style.display = "flex";
  //   toggleNav();
  // }
  //
  console.log(nav.style);

  if (nav.style.display == "") {
    nav.style.display = "flex";
  }
  if (nav.style.display == "none") {
    nav.style.display = "flex";
  } else {
    nav.style.display = "none";
  }
}

function createFormInput(form, id, name, type, value) {
  const obj = document.createElement("input");
  obj.id = id;
  obj.type = type;
  obj.name = name;
  obj.value = value;
  form.appendChild(obj);
}
function createFormDatalist(form, id, name, listname, value) {
  const obj = document.createElement("input");
  obj.id = id;
  obj.name = name;
  obj.value = value;
  obj.setAttribute("list", listname);
  form.appendChild(obj);
}
function createFormCheckbox(form, id, name, type, checked, label) {
  const obj = document.createElement("input");
  const lab = document.createElement("label");
  lab.innerHTML = label;
  lab.id = id;
  obj.id = id;
  obj.type = type;
  obj.name = name;
  obj.checked = checked;
  form.appendChild(obj);
  form.appendChild(lab);
}
function removeFormInput(parentObject, id) {
  var obj = document.getElementById(id);
  if (obj) {
    parentObject.removeChild(obj);
  }
}
function createFormSelect(form, id, name) {
  var element = document.createElement("select");
  element.id = id;
  element.name = name;
  form.appendChild(element);
  return element;
}

function createSelectOption(obj_select, value) {
  var option = document.createElement("option");
  option.value = value;
  option.text = value;
  obj_select.appendChild(option);
}

function toggleObjectInputs(formid) {
  const form = document.getElementById(formid);
  const typeSelect = document.getElementById("obj_type");
  var brTags = form.getElementsByTagName("br");
  for (var i = 0; i < brTags.length; i++) {
    form.removeChild(brTags[i]);
  }

  if (typeSelect.value === "") {
    removeFormInput(form, "obj_cores");
    removeFormInput(form, "obj_memsize");
    removeFormInput(form, "obj_disksize");
    removeFormInput(form, "obj_kb");
    removeFormInput(form, "obj_name");
    removeFormInput(form, "obj_ostype");
    removeFormInput(form, "obj_cephpublic");
    removeFormInput(form, "obj_cephshared");
    removeFormInput(form, "obj_cephuser");
    removeFormInput(form, "obj_cephpublic");
    removeFormInput(form, "obj_cephshared");
    removeFormInput(form, "obj_cephuser");
    removeFormInput(form, "obj_cephpool");
    removeFormInput(form, "obj_cephpool");
    removeFormInput(form, "obj_rootimage");
    removeFormInput(form, "obj_dockerfile");
    removeFormInput(form, "obj_contype");
    removeFormInput(form, "obj_resolution");
    removeFormInput(form, "obj_viewermodes");
    removeFormInput(form, "obj_viewerscale");
    removeFormInput(form, "obj_viewerscale");
  }
  if (typeSelect.value === "container") {
    removeFormInput(form, "obj_cores");
    removeFormInput(form, "obj_memsize");
    removeFormInput(form, "obj_disksize");
    removeFormInput(form, "obj_name");
    removeFormInput(form, "obj_cores");
    removeFormInput(form, "obj_memsize");
    removeFormInput(form, "obj_disksize");
    removeFormInput(form, "obj_kb");
    removeFormInput(form, "obj_ostype");
    removeFormInput(form, "obj_cephpool");
    removeFormInput(form, "obj_cephpool");
    removeFormInput(form, "obj_cephpublic");
    removeFormInput(form, "obj_cephshared");
    removeFormInput(form, "obj_cephuser");
    removeFormInput(form, "obj_cephpublic");
    removeFormInput(form, "obj_cephshared");
    removeFormInput(form, "obj_cephuser");
    removeFormInput(form, "obj_contype");
    removeFormInput(form, "obj_resolution");
    removeFormInput(form, "obj_viewermodes");
    removeFormInput(form, "obj_viewerscale");
    removeFormInput(form, "obj_viewerscale");
    createFormInput(form, "obj_name", "name", "text", "testname");
    var element = createFormSelect(form, "obj_rootimage", "rootimage");
    createSelectOption(element, "x11vnc");
    createSelectOption(element, "wine");
    form.appendChild(document.createElement("br"));
    createFormInput(form, "obj_cores", "cores", "text", "2");
    createFormInput(form, "obj_memsize", "memsize", "text", "2048");
    createFormInput(form, "obj_disksize", "disksize", "text", "8");
    createFormInput(form, "obj_dockerfile", "dockerfile", "file", "");
    form.appendChild(document.createElement("br"));
    createFormCheckbox(
      form,
      "obj_cephpublic",
      "ceph_public",
      "checkbox",
      false,
      "CFS_Public",
    );
    createFormCheckbox(
      form,
      "obj_cephshared",
      "ceph_shared",
      "checkbox",
      false,
      "CFS_Shared",
    );
    createFormCheckbox(
      form,
      "obj_cephuser",
      "ceph_user",
      "checkbox",
      false,
      "CFS_User",
    );
    createFormDatalist(
      form,
      "obj_contype",
      "viewer_contype",
      "arglistcontypedocker",
      "",
    );
    createFormDatalist(
      form,
      "obj_resolution",
      "viewer_resolution",
      "arglistresize",
      "",
    );
    createFormDatalist(
      form,
      "obj_viewermodes",
      "viewer_resize",
      "arglistviewmodes",
      "",
    );
    form.appendChild(document.createElement("br"));
    createFormCheckbox(
      form,
      "obj_viewerscale",
      "viewer_scale",
      "checkbox",
      false,
      "Scale",
    );
  } else if (typeSelect.value === "vm") {
    removeFormInput(form, "obj_cores");
    removeFormInput(form, "obj_memsize");
    removeFormInput(form, "obj_disksize");
    removeFormInput(form, "obj_name");
    removeFormInput(form, "obj_rootimage");
    removeFormInput(form, "obj_dockerfile");
    removeFormInput(form, "obj_cephpublic");
    removeFormInput(form, "obj_cephshared");
    removeFormInput(form, "obj_cephuser");
    removeFormInput(form, "obj_cephpublic");
    removeFormInput(form, "obj_cephshared");
    removeFormInput(form, "obj_cephuser");
    removeFormInput(form, "obj_contype");
    removeFormInput(form, "obj_resolution");
    removeFormInput(form, "obj_viewermodes");
    removeFormInput(form, "obj_viewerscale");
    removeFormInput(form, "obj_viewerscale");
    createFormInput(form, "obj_name", "name", "text", "testname");
    var element = createFormSelect(form, "obj_ostype", "os_type");
    createSelectOption(element, "win10");
    createSelectOption(element, "win11");
    createSelectOption(element, "l26");
    form.appendChild(document.createElement("br"));
    createFormInput(form, "obj_cores", "cores", "text", "4");
    createFormInput(form, "obj_memsize", "memsize", "text", "4096");
    createFormInput(form, "obj_disksize", "disksize", "text", "64");
    createFormInput(form, "obj_kb", "kb", "text", "de");
    form.appendChild(document.createElement("br"));
    createFormCheckbox(
      form,
      "obj_cephpool",
      "ceph_pool",
      "checkbox",
      false,
      "CEPH_RBD",
    );
    form.appendChild(document.createElement("br"));
    createFormCheckbox(
      form,
      "obj_cephpublic",
      "ceph_public",
      "checkbox",
      false,
      "CFS_Public",
    );
    createFormCheckbox(
      form,
      "obj_cephshared",
      "ceph_shared",
      "checkbox",
      false,
      "CFS_Shared",
    );
    createFormCheckbox(
      form,
      "obj_cephuser",
      "ceph_user",
      "checkbox",
      false,
      "CFS_User",
    );
    createFormDatalist(
      form,
      "obj_contype",
      "viewer_contype",
      "arglistcontype",
      "",
    );
    createFormDatalist(
      form,
      "obj_resolution",
      "viewer_resolution",
      "arglistresize",
      "",
    );
    createFormDatalist(
      form,
      "obj_viewermodes",
      "viewer_resize",
      "arglistviewmodes",
      "",
    );
    form.appendChild(document.createElement("br"));
    createFormCheckbox(
      form,
      "obj_viewerscale",
      "viewer_scale",
      "checkbox",
      false,
      "Scale",
    );
  }
}
function updateTasklistInputs(formid, tasklistid) {
  hidden = document.getElementById(tasklistid);
  form = document.getElementById(formid);
  if (!form | !hidden) {
    console.error("DID NOT GET ALL REQUIRED ELEMENTS");
    return;
  }

  const divs = form.getElementsByClassName("taskdiv");
  const data = [];
  for (const div of divs) {
    const el_select = div.querySelector("select");
    const el_cmd = div.querySelector('input[name="cmd"]');
    const el_args = div.querySelector('input[name="args"]');
    if (el_select && el_cmd && el_args) {
      const cmd = el_cmd.value;
      const type = el_select.value;
      const args = el_args.value;
      const combined = { type, cmd, args };
      if (type !== "" && cmd !== "") {
        data.push(combined);
      }
    }
  }
  jsonData = JSON.stringify(data);
  hidden.value = jsonData;
}

function updateApplistInputs(formid, applistid) {
  hidden = document.getElementById(applistid);
  form = document.getElementById(formid);
  if (!form | !hidden) {
    console.error("DID NOT GET ALL REQUIRED ELEMENTS");
    return;
  }

  const divs = form.getElementsByClassName("cmddiv");
  const data = [];
  for (const div of divs) {
    const select = div.querySelector("select");
    const input = div.querySelector("input");
    if (select && input) {
      const cmd = select.value;
      const name = select.options[select.selectedIndex].text;
      const args = input.value;
      const combined = { name, cmd, args };
      if (name !== "" && cmd !== "") {
        data.push(combined);
      }
    }
  }
  jsonData = JSON.stringify(data);
  hidden.value = jsonData;
}
function updateTargetInputs(formid, targetid) {
  hidden = document.getElementById(targetid);
  form = document.getElementById(formid);
  if (!form | !hidden) {
    console.error("DID NOT GET ALL REQUIRED ELEMENTS");
    return;
  }
  const name = form.querySelector('input[name="name"]');
  const cmd = form.querySelector('input[name="cmd"]');
  const args = form.querySelector('input[name="args"]');
  const combined = { name: name.value, cmd: cmd.value, args: args.value };
  jsonData = JSON.stringify(combined);
  hidden.value = jsonData;
}
document.onreadystatechange = () => {
  if (document.readyState === "interactive") {
    const conElement = document.getElementById("dashboard-connections");
    conElement.onchange = function (event) {
      if (conElement.value !== "") {
        setViewerInstance();
      } else {
        document.getElementById("viewerurl").value = "";
        document.getElementById("viewer").setAttribute("src", "");
      }
    };
  }
};
