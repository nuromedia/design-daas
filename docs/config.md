# Configuration options

The web app and Proxmox adapters are configured via the `*.toml` files
in the `src.config` folder.
The corresponding code is in `src.app` and `src.scripts`.

## Config file location

Configuration must be placed in a `*.toml` file in the config directory.
There is a `*.toml` file for each component that can be adapted.

## Config file syntax

This file uses the [TOML](https://toml.io/en/) format,
which provides an INI-style syntax for a JSON-style data model.
Here, the advantage is that the config can contain comments,
and is neatly separated into multiple sections.

Example snippet:

```toml
# can have comments
[web]
database = "/some/path"
```

This corresponds to the JSON data structure:

```json
{
  "web": {
    "database": "/some/path"
  }
}
```

## Config file schema

The schema of the config files is validated,
and unsupported keys will raise an error (to prevent typos).
