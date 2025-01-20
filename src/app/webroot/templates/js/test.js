var counter = 0;
var setBegin = 0;
var results_single = [];
var results_all = {};
var expected_results = 0;
var expected_jobs = 3;
var testname = "";
var testurl = "";
var running = false;
var closeAfterFinished = false;
var testobject = "contx11";
// var testobject = "vmDeb12";
var testapp = "deb12CalcApp";
var testfile = "deb12DummyFile";
var testenv = "oHGslCee3yr2P8LsPFKgXA";
var testcon = "random_con_id";
var testinstance = "randomkey";
var testowner = 0;
var testid = testobject;

class CSVDownloader {
  constructor(name, data) {
    this.name = name;
    this.data = data;
  }

  downloadCSV() {
    const blob = new Blob([this.data], { type: "text/csv" });
    const link = document.createElement("a");
    link.download = this.name + ".csv";
    link.href = window.URL.createObjectURL(blob);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}
class FormHandler {
  constructor(options) {
    this.options = options;
  }

  async handleSubmit(event, closeMe) {
    event.preventDefault();

    closeAfterFinished = closeMe;
    this.initJobs();
    this.nextJob();
  }

  initJobs() {
    const txtAmount = document.getElementById("amount");
    const txtUrl = document.getElementById("url");
    const resultdiv = document.getElementById("results");
    resultdiv.innerHTML = "";

    results_all = {};
    expected_results = parseInt(txtAmount.value);
    testurl = txtUrl.value;
  }
  nextJob() {
    const currentSize = Object.keys(results_all).length;
    if (currentSize === 0) {
      this.fetchMulti(expected_results, testurl);
    } else if (currentSize === 1) {
      this.fetchAsyncAwait(expected_results, testurl);
    } else if (currentSize === 2) {
      this.fetchAsyncNowait(expected_results, testurl);
    } else {
      console.log("All jobs executed");
    }
  }
  async fetchAsyncAwait(amount, url) {
    this.initTestParams("firefox-await", amount, url);
    for (let index = 0; index < amount; index++) {
      const data = {
        id: testid,
        id_instance: testinstance,
        id_owner: testowner,
        counter: counter++,
        timestamp: Date.now(),
      };
      const result = await this.do_fetch_async_await(data, url);
      if (result !== null) {
        this.storeResult(result);
      }
    }
  }
  fetchAsyncNowait(amount, url) {
    this.initTestParams("firefox-nowait", amount, url);
    for (let index = 0; index < amount; index++) {
      const data = {
        id: testid,
        id_instance: testinstance,
        id_owner: testowner,
        counter: counter++,
        timestamp: Date.now(),
      };
      this.do_fetch_async_nowait(data, url);
    }
  }
  fetchMulti(amount, url) {
    this.initTestParams("firefox-promises", amount, url);
    var urls = [];
    const token = window.localStorage.getItem("token");
    for (let index = 0; index < amount; index++) {
      urls[index] = url;
    }
    var requests = urls.map(async function (url) {
      const data = {
        id: testid,
        id_instance: testinstance,
        id_owner: testowner,
        counter: counter++,
        timestamp: Date.now(),
      };
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify(data),
      };

      return fetch(url, options).then(function (response) {
        return response.json();
      });
    });
    Promise.all(requests)
      .then((array) => {
        for (let index = 0; index < array.length; index++) {
          const element = array[index];
          this.storeResult(element);
        }
      })
      .catch(function (err) {
        console.log(err);
      });
  }
  async do_fetch_async_await(data, url) {
    try {
      const token = window.localStorage.getItem("token");
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify(data),
      });
      return await response.json();
    } catch (error) {
      console.error("Async fetch error:", error);
    }
    return null;
  }
  do_fetch_async_nowait(data, url) {
    const token = window.localStorage.getItem("token");
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        return response.json();
      })
      .then((json) => {
        this.storeResult(json);
      });
  }

  storeResult(element) {
    var result = {};
    var ts_diff = 0;
    var delay_backend = 0;
    const ts_end = Date.now();
    if (typeof element["http_params_form"] !== "undefined") {
      if (typeof element["http_params_form"]["timestamp"] !== "undefined") {
        const ts_begin = element["http_params_form"]["timestamp"];
        ts_diff = ts_end - ts_begin;
        const setTime = ts_end - setBegin;
        const rps = 1000 / ts_diff;
        if (
          typeof element["timings"] !== "undefined" &&
          typeof element["timings"]["request"] !== "undefined"
        ) {
          const backend_end = parseInt(element["timings"]["request"].end);
          if (backend_end !== 0) {
            delay_backend = ts_end - backend_end;
          }
        }
        result = {
          result: element,
          ts_begin: ts_begin,
          ts_end: ts_end,
          ts_diff: ts_diff,
          rps: parseFloat(rps.toFixed(2)),
          delay_backend: delay_backend,
        };
      } else {
        result = {
          result: element,
          ts_begin: 0,
          ts_end: 0,
          ts_diff: 0,
          rps: 0,
          delay_backend: 0,
        };
      }
    }

    // console.log("SINGLE: " + JSON.stringify(result));
    results_single.push(result);
    if (results_single.length === expected_results) {
      this.finalizeResults();
    }
  }
  finalizeResults() {
    var diffs = 0;
    var delay_cli = 0;
    var delay_bck = 0;
    var proc_time = 0;
    var auth_time = 0;
    var ctx_time = 0;
    var minBegin = Date.now();
    var maxEnd = 0;

    for (let index = 0; index < expected_results; index++) {
      const element = results_single[index];
      diffs += element.ts_diff;
      if (typeof element["delay_backend"] !== "undefined") {
        delay_bck += element.delay_backend;
        if (
          typeof element["result"] !== "undefined" &&
          typeof element["result"]["timings"] !== "undefined"
        ) {
          delay_cli += element.result.timings.request_delay;
          ctx_time += element.result.timings.context.diff;
          proc_time += element.result.timings.processing.diff;
          auth_time += element.result.timings.authentication.diff;
          minBegin = Math.min(minBegin, element.ts_begin);
          maxEnd = Math.max(maxEnd, element.ts_end);
        }
      }
    }
    var total_time = maxEnd - minBegin;
    var ratio_diffs = diffs / expected_results;
    var ratio_cli = delay_cli / expected_results;
    var ratio_bck = delay_bck / expected_results;
    var ratio_ctx = ctx_time / expected_results;
    var ratio_proc = proc_time / expected_results;
    var ratio_auth = auth_time / expected_results;
    var requests_per_second = 1000 / ratio_diffs;
    requests_per_second = parseFloat(requests_per_second.toFixed(2));

    results_all[testname] = {
      name: testname,
      results: results_single,
      total_time: total_time,
      sum_diff: diffs,
      sum_ctx: ctx_time,
      sum_auth: auth_time,
      sum_proc: proc_time,
      sum_delay_cli: delay_cli,
      sum_delay_bck: delay_bck,
      requests_per_second: requests_per_second,
      ratio_diffs: ratio_diffs,
      ratio_ctx: ratio_ctx,
      ratio_auth: ratio_auth,
      ratio_proc: ratio_proc,
      ratio_cli: ratio_cli,
      ratio_bck: ratio_bck,
    };
    console.log(
      "Gathered " +
        expected_results +
        " results. Testrun finalized (" +
        testname +
        ") => " +
        requests_per_second,
    );

    if (Object.keys(results_all).length === expected_jobs) {
      console.log("All " + expected_jobs + " jobs finished");
      const values = Object.values(results_all);
      for (let index = 0; index < values.length; index++) {
        const el = values[index];
        this.convertToCsv(el);
      }

      running = false;
      if (closeAfterFinished === true) {
        setTimeout(function () {
          window.close();
        }, 2000);
      }
    } else {
      running = false;
      setTimeout(this.nextJob.bind(this), 1000);
    }
  }
  convertToCsv(result) {
    const resultdiv = document.getElementById("results");
    const msg =
      result.ratio_diffs +
      "ms," +
      result.ratio_cli +
      "ms," +
      result.ratio_bck +
      "ms : Context: " +
      result.ratio_ctx +
      "ms : Proc: " +
      result.ratio_proc +
      "ms, Auth: " +
      result.ratio_auth +
      "ms => " +
      result.requests_per_second +
      " R/S " +
      "(" +
      result.name +
      ")";
    console.log(msg);

    const setname = result.name;
    const resultset = result.results;
    const elements = Object.values(resultset);

    var out = "";

    var headers =
      "CNT,TS_BEGIN,TS_END,RPS,DIFF,DELAY_CLI,DELAY_BCK,CTXTIME,PROCTIME,AUTHTIME";
    var data = headers + "\n";
    resultdiv.innerHTML += headers + "<br/>";
    for (let index = 0; index < elements.length; index++) {
      const el = elements[index];

      if (typeof el["result"] !== "undefined") {
        var line = el.result.http_params_form.counter + ",";
        line +=
          el.ts_begin + "," + el.ts_end + "," + el.rps + "," + el.ts_diff + ",";
        if (
          typeof el.result !== "undefined" &&
          typeof el.result.timings !== "undefined"
        ) {
          line += el.result.timings.request_delay + "," + el.delay_backend;
          if (
            typeof el.result.timings.context !== "undefined" &&
            typeof el.result.timings.processing !== "undefined" &&
            typeof el.result.timings.authentication !== "undefined"
          ) {
            line +=
              "," +
              el.result.timings.context.diff +
              "," +
              el.result.timings.processing.diff +
              "," +
              el.result.timings.authentication.diff +
              "\n";
          } else {
            line += "\n";
          }
        } else {
          line += "0,0,0,0,0\n";
        }
        out += line.replace(/\n/g, "<br />");
        data += line;
      }
    }
    resultdiv.innerHTML += out + "<b>=>" + msg + "</b><br/><br/>";
    const downloader = new CSVDownloader(setname, data);
    downloader.downloadCSV();
  }
  initTestParams(name, amount, url) {
    counter = 0;
    setBegin = Date.now();
    results_single = [];
    expected_results = amount;
    testname = name + "-" + expected_results + "-" + url.replace(/\//g, "");
    running = true;
  }
}

async function onBodyLoad(event, closeWhenFinished) {
  await doLogin(false);
  handler = new FormHandler({ async: false });
  handler.handleSubmit(event, closeWhenFinished);
}
async function doSubmit(event, closeWhenFinished) {
  handler = new FormHandler({ async: false });
  handler.handleSubmit(event, closeWhenFinished);
}
