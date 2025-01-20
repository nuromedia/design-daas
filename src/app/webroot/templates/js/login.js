const url = "https://backend.application.daas-design.de/oauth2/user/token";
async function doLogin(forward) {
  const user = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const clientid = document.getElementById("clientid").value;
  var scope = "user";
  if (document.getElementById("adminscope").checked) {
    scope = "admin";
  }
  const authResult = await do_fetch_async_await(
    {
      username: user,
      password: password,
      client_id: clientid,
      scope: scope,
      grant_type: "password",
    },
    url,
  );
  if (authResult !== null) {
    if (typeof authResult["access_token"] !== "undefined") {
      const token = authResult["access_token"];
      if (token !== "") {
        window.localStorage.setItem("auth", JSON.stringify(authResult));
        window.localStorage.setItem("token", token);
        console.log("AUTH Success");
        if (forward === true) {
          const form = document.getElementById("formid");
          const bearer = document.getElementById("bearer");
          bearer.value = token;
          form.submit();
        }
      }
    }
  }
}
async function do_fetch_async_await(data, url) {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    return await response.json();
  } catch (error) {
    console.error("Async fetch error:", error);
  }
  return null;
}
