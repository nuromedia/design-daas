# Rest API

This document provides an overview of all routes.

Technically, most of these routes are not REST APIs.

## Browser routes

Some routes provide HTML responses and are intended to be navigated to with the browser.

### GET `/` {#get-root}

The user interface for listing, starting, and stopping apps/instances.

### POST `/app/:id`

Creates a new instance of that application.
It redirects to the instance URL.

### GET `/instance/:id`

Shows a viewer for the instance.

### GET `/login`

### POST `/login`

Form for logging in.
Other routes redirect to this endpoint if they require authentication.
Upon successful authentication, this route redirects back.

### POST `/logout`

Remove log-in information from the session cookie, logging the user out.

## API routes

These routes are intended to be invoked via JS client code, e.g. via `fetch()`.

### WS `/instance/:id`

Provide a websocket for the Guacamole proxy.
Available if the instance uses a Guacamole connection.

### DELETE `/instance/:id`

Stop the instance.
