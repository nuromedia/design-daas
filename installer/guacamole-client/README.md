## guacamole-client

This directory builds the Guacamole-Common JavaScript library.

## How to use

1. Run `make`
2. Use the resulting `guacamole.js` file

## Technical details

The folder `upstream` contains the Guacamole-Client repository as a Git Submodule.

* https://github.com/apache/guacamole-client
* https://git-scm.com/book/en/v2/Git-Tools-Submodules

The Makefile will set this up automatically.

The Apache Guacamole-Client library contains the JavaScript code in the directory
`guacamole-common-js/src/main/webapp/modules/*.js`.

Unfortunately, these files do not use any reasonably modern JS module pattern,
and instead use jQuery-style globals:

```js
var Guacamole = Guacamole || {};

Guacamole.Foo = ...;
```

So it's not possible to use modern JS tooling such as Webpack or Rollup
to bundle this into a single file.

The Guacamole code uses the Google Closure compiler for bundling,
but for our purposes the `cat` command is sufficient.
This could be minified in the future.
