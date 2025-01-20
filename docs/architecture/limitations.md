# Limitations of the architecture

This project is mostly prototype-level code, so there are lots of limitations.
However, there are clear paths to solve them, if that should become necessary.

## Features

Lots of features intended to be part of the final DESIGN architecture are not yet available. Importantly:

- no user management
- no VM support (being worked on)
- no application lifecycle (environments, deployments, applications)

## Scalability and Performance

The main workload in the DaaS system is in the actual containers and VMs running applications.
Compared to that, the REST API requires negligible resources.
Thus, scalability arguments are likely to be premature.

However, there are two potential problem areas in this architecture:

- the database is embedded
- the proxy component is on a performance-critical path

## Database limitations

The current database uses SQLite.
This might be awkward to work with.
It also means that the database engine runs in-process, precluding horizontal scaling.
Another consequence is that if other components want to store persistent data, APIs for this must be exposed – external access to the DB is not possible.

Having to write raw SQL can be avoided by switching to an ORM or query builder like Python's [SQLAlchemy](https://www.sqlalchemy.org/).

Scalability concerns could be addressed by switching to a different database.
To do that, the SQLite-specific details would have to be removed from the database class,
and swapped for a different database connector.

Careful: any replacements of the database must also support async operations in order to avoid locking up the proxy.

If any changes to the database have to be made,
the good news is that only the database module has to be touched.
No other code contains database-specific operations.

## Proxy limitations

The proxy has limitations along two directions:
the WebSocket connection relies on asynchronous operations for low latencies,
and the Guacamole proxy must fully parse each individual message.

## Proxy must be asynchronous

It is unavoidable that the proxy component must be asynchronous:
the server must push events such as screen updates to the client.
Since the client is browser-based, this must be a web protocol.
The only available protocol for that is WebSocket.

Writing WebSocket-capable servers is more difficult than an ordinary HTTP server,
since it must be event-based, must be asynchronous.
In Python, this requires a web framework that builds upon the ASGI ecosystem.
Here, we've picked Quart.

The limitation in this context is that `async` code is infectious.
In order for the async proxy to behave as expected,
there must not be synchronous code blocking the event loop.
In particular, all requests to external resources (Docker, Proxmox, databases)
must be performed on a background thread.
Quart offers the `run_sync()` utility for this purpose,
but it's easy to forget.

There's also the problem that Guacamole proxy events are competing with other work in the event loop.
If too much other work is happening, performance of the proxy might degrade,
potentially leading to stuttering or other latency effects.

If this becomes a problem,
the proxy and the management-API components have to be split up into separate servers.
To do this, the management server would have to provide internal APIs
from which the proxy server can retrieve credentials etc.

## Guacamole message parsing

The Guacamole protocol was designed to be easy to parse by high-level languages like JavaScript and Java.
But alas, Unicode makes everything more complex,
and it is definitely not easy to handle correctly.
While the protocol uses the sensible `LENGHT CONTENT` Hollerith-String encoding,
the length is given in terms of Unicode codepoints, not in terms of bytes.
Also, this encoding only relates to individual fields,
but each message is made up of an indeterminate number of fields.

The proxy cannot just forward the stream of messages,
but must parse each one of them:

- For the handshake, the proxy must participate in the protocol and read messages.

- The JS client has a weak assumption that it will only receive complete messages,
  thus messages from Guacd should be buffered until they can be forwarded in a single WebSocket frame.

- The JavaScript client can send `ping` messages.
  This ping command is an internal protocol extension of the JS client,
  and not handled by the Guacd component.
  Thus, our proxy must respond to the ping messages on its own.

- Other messages might have to be intercepted as well,
  e.g. to handle `size` messages which Guacd doesn't implement for VNC connections.

So, all messages have to be parsed.

Due to the protocol complexity, this requires byte-by-byte parsing.
The Python code for this is absolutely not efficient.
Maybe it can be optimized,
maybe it can be rewritten to be JIT-compiled with Numba,
maybe that code has to be replaced with a native component (e.g. using PyO3).
