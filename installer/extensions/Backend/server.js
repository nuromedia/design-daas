const GuacamoleLite = require('guacamole-lite');
const express = require('express');
const http = require('http');

const app = express();

const server = http.createServer(app);

const guacdOptions = {
    host: '192.168.178.31',
    //host: 'localhost',
    port: 4822
};

const clientOptions = {
    crypt: {
        cypher: 'AES-256-CBC',
        key: 'MySuperSecretKeyForParamsToken12'
    }
    // Logs
    /*,log: {
        level: 'Debug',
        stdLog: (...args) => {
            console.log('[MyLog]', ...args)
        },
        errorLog: (...args) => {
            console.error('[MyLog]', ...args)
        }
    }
    // End Logs*/
};

const callbacks = {
    processConnectionSettings: (settings, callback) => {
        if (settings['expiration'] < Date.now()) {
            console.error('Token expired');
            return callback(new Error('Token expired'));
        }
        //console.log("testalex"+JSON.stringify(settings, null, 2));
        //settings.connection['drive-path'] = '/tmp/guacamole_' + settings['userId'];
        callback(null, settings);
    }
};

const guacServer = new GuacamoleLite(
    {server},
    guacdOptions,
    clientOptions,
    callbacks
);

server.listen(8080);