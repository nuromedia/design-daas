# `daas_web` Documentation

Documentation for the `qweb` server code of the DaaS-DESIGN project:
<https://daas-design.de/>

## Where to start

- [whole system overview](backend-overview.md)
- high-level [architecture](architecture/README.md) explanation
- [Authentication](authentication.md) explanation
- low level Python API documentation of the [`qweb` module](docs/reference/app/index.html)
  (drill down to specific modules in the sub-navigation)

## Building the docs

These docs use [mkdocs](https://www.mkdocs.org).

- `mkdocs new [dir-name]` - Create a new project.
- `mkdocs serve` - Start the live-reloading docs server.
- `mkdocs build` - Build the documentation site.
- `mkdocs -h` - Print help message and exit.

Relevant files:

- `mkdocs.yml` contains configuration
- `docs/` contains documentation pages
- `src/app` contains the code from which API docs are created
