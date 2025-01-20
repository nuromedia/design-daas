class Size {
  width = 0;
  height = 0;
  hasExtend = false;
  constructor(width, height) {
    this.width = parseFloat(width);
    this.height = parseFloat(height);
    this.hasExtend = false;
    if (this.width !== 0 || this.height !== 0) {
      this.hasExtend = true;
    }
  }
  equals(other) {
    var result = false;
    if (this.width === other.width && this.height === other.height) {
      result = true;
    }
    return result;
  }
  diff(other) {
    var result;
    if (this.equals(other)) {
      result = new Size(0, 0);
    } else {
      const diffWidth = Math.abs(this.width - other.width);
      const diffHeight = Math.abs(this.height - other.height);
      result = new Size(diffWidth, diffHeight);
    }
    return result;
  }
  fromString(str) {
    const arr = str.split("x");
    this.width = parseFloat(arr[0]);
    this.height = parseFloat(arr[1]);
  }
  toString() {
    return Math.floor(this.width) + "x" + Math.floor(this.height);
  }
  toJSON() {
    return { width: this.width, height: this.height };
  }
  str() {
    return JSON.stringify(this);
  }
}

class BackendService {
  constructor(baseURL, defaultMaxRetries = 3, retryDelay = 1000) {
    this.baseURL = baseURL;
    this.defaultMaxRetries = defaultMaxRetries;
    this.retryDelay = retryDelay; // delay in milliseconds between retries
  }

  async query(
    url,
    method = "GET",
    headers = {},
    data = null,
    maxRetries = this.defaultMaxRetries,
  ) {
    const options = {
      method,
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        ...headers,
      },
    };

    if (data) {
      options.body = new URLSearchParams(data).toString();
    }

    let attempts = 0;
    while (attempts < maxRetries) {
      try {
        const response = await fetch(this.baseURL + url, options);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        return result;
      } catch (error) {
        attempts += 1;

        if (attempts >= maxRetries) {
          this.handleMaxRetriesReached(url, method, headers, data);
          throw error; // Re-throw the error after max retries are reached
        }

        await this.delay(this.retryDelay); // Wait before next retry
      }
    }
  }

  delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  handleMaxRetriesReached(url, method, headers, data) {}

  async checkInstance(id_instance, token) {
    const url = `/viewer/check/${id_instance}`;
    const method = "POST";
    const data = { token };

    try {
      const result = await this.query(url, method, {}, data);
      return result;
    } catch (error) {
      throw error;
    }
  }
  async getInfo(id_instance, token, resolutions) {
    const url = `/viewer/info/${id_instance}`;
    const method = "POST";
    var data = { token };
    if (resolutions === true) {
      data = { token, resolutions };
    }
    try {
      const result = await this.query(url, method, {}, data);
      return result;
    } catch (error) {
      throw error;
    }
  }
  async setScreenInfo(id_instance, token, contype, resolution, resize, scale) {
    const url = `/viewer/set_screen/${id_instance}`;
    const method = "POST";
    var data = { token, contype, resolution, resize, scale };
    try {
      const result = await this.query(url, method, {}, data);
      return result;
    } catch (error) {
      throw error;
    }
  }
}

class ResolutionTools {
  constructor() {}
  findNativeResolution(bounds, resolutions) {
    var result = new Size(640, 480);
    if (resolutions !== null) {
      for (let index = 0; index < resolutions.length; index++) {
        const res = resolutions[index];
        if (res !== "max") {
          const testsize = new Size(0, 0);
          testsize.fromString(res);
          if (
            testsize.width <= bounds.width &&
            testsize.height <= bounds.height
          ) {
            result = testsize;
            break;
          }
        }
      }
    }
    return result;
  }
  isNativeResolution(bounds, resolutions) {
    var result = false;
    if (resolutions !== null) {
      for (let index = 0; index < resolutions.length; index++) {
        const res = resolutions[index];
        if (res === bounds.toString()) {
          result = true;
          break;
        }
      }
    }
    return result;
  }
}
