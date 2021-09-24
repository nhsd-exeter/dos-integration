const process = require("process");
const https = require("https");
const fs = require("fs");
const express = require("express");

process.on("SIGINT", function () {
  process.exit();
});

const app = express();
app.get("/", function (req, res) {
  res.send("node");
});

const host = "0.0.0.0";
const port = 8443;
const options = {
  key: fs.readFileSync("/certificate/certificate.key"),
  cert: fs.readFileSync("/certificate/certificate.crt"),
};

https.createServer(options, app).listen(port, host);
