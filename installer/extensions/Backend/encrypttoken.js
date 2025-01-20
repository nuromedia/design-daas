const crypto = require('crypto');

const CIPHER = 'aes-256-cbc';
const SECRET_KEY = 'MySuperSecretKeyForParamsToken12';

//Windows RDP
const tokenObject = {
    connection: {
        type: "rdp",
        settings: {
            "hostname": "192.168.178.30",
            "username": "alex",
            "password": "win10",
            "enable-drive": true,
            "drive-path": '/tmp/alex',
            "create-drive-path": true,
            "security": "any",
            "ignore-cert": true,
            "enable-wallpaper": false,
            "enable-printing": true,
            "audio": ["audio/L8", "audio/L16"],
            "enable-audio-input": true
        }
    }
};

// Linux vnc
/*const tokenObject = {
    connection: {
        type: "vnc",
        settings: {
            "hostname": "192.168.178.28",
            "username": "alex",
            "password": "vnc",
            "security": "any",
            "ignore-cert": true,
            "reverse-connect": true,
            "enable-audio": true,
            "audio-servername": "192.168.178.28"
        }
    }
};*/

function encryptToken(value) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(CIPHER, Buffer.from(SECRET_KEY), iv);

    let encrypted = cipher.update(JSON.stringify(value), 'utf8', 'base64');
    encrypted += cipher.final('base64');

    const data = {
        iv: iv.toString('base64'),
        value: encrypted
    };

    const json = JSON.stringify(data);
    return Buffer.from(json).toString('base64');
}

// Encrypt the tokens


const originalToken = JSON.stringify(tokenObject, null, 2);
const token = encryptToken(tokenObject);
const urlencodedToken = encodeURIComponent(token);

console.log(`${urlencodedToken}`)