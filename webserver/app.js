const express = require('express');
const path = require('path');
const WebSocket = require("ws");
var fs = require('fs');
const app = express();
const http = require('http');
const url = require('url');
const querystring = require('querystring');  


const WEBSOCKETPATH = process.env.WEBSOCKETPATH  || '/control';
const WEBSOCKETVIDEOPATH = process.env.WEBSOCKETPATH  || '/video';
const SECRETTOKEN = process.env.SECRETTOKEN || 'token';


// =================================
// Web server
const server = require('http').Server(app);

// -------------------------
app.use(express.static(path.resolve(__dirname, './build')));

// -------------------------
// All other GET requests not handled before will return our React app
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, './build', 'index.html'));
});


// =================================
// Set up the WebSocket server  
const wss1 = new WebSocket.Server( {noServer: true });  
const wss2 = new WebSocket.Server( {noServer: true });  


// Create unique id
wss1.getUniqueID = function () {
  function s4() {
      return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
  }
  return s4() + s4() + s4();
};


// Create unique id
wss2.getUniqueID = function () {
  function s4() {
      return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
  }
  return s4() + s4() + s4();
};



// =================================
// For handling controls ans sensors (jsons)
wss1.on('connection', function connection(ws, request) {

  const parsedUrl = url.parse(request.url);  
  const queryParams = querystring.parse(parsedUrl.query);  

  ws.id = `${wss1.getUniqueID()}-${queryParams.robotid}-${queryParams.type}`

  console.log(`new control connection of type ${queryParams.type} ${ws.id} <=> ${queryParams.robotid}`)


  ws.on('message', function message(data, isBinary) {
    wss1.clients.forEach(function each(client) {
      if (
        client !== ws && 
        client.readyState === WebSocket.OPEN &&
        client.id.split('-')[1] === ws.id.split('-')[1] &&
        client.id.split('-')[2] !== ws.id.split('-')[2]
      ) {

        // We broadcast messages to other clients with the same robotId but not the same type
        client.send(data, { binary: isBinary });
      }
    });
  });

  // Websockets
  ws.on('error', console.error);
  ws.on('close', function close() {  console.log(`client ${ws.id} disconnected!`)});
  
});

// =================================
// For handling binary video data
wss2.on('connection', function connection(ws, request) {

  const parsedUrl = url.parse(request.url);  
  const queryParams = querystring.parse(parsedUrl.query);  

  ws.id = `${wss2.getUniqueID()}-${queryParams.robotid}-${queryParams.type}`

  console.log(`new video connection of type ${queryParams.type} ${ws.id} <=> ${queryParams.robotid}`)

  ws.on('message', function message(data, isBinary) {
    wss2.clients.forEach(function each(client) {
      if (
        client !== ws && 
        client.readyState === WebSocket.OPEN &&
        client.id.split('-')[1] === ws.id.split('-')[1] &&
        client.id.split('-')[2] !== ws.id.split('-')[2]
      ) {

        // We broadcast messages to other clients with the same robotId but not the same type
        client.send(data, { binary: isBinary });
      }
    });
  });

  // Websockets
  ws.on('error', console.error);
  ws.on('close', function close() {  console.log(`client ${ws.id} disconnected!`)});
  
});


// =================================
server.on('upgrade', function upgrade(request, socket, head) {

  const parsedUrl = url.parse(request.url);  
  const { pathname } = parsedUrl;  
  const queryParams = querystring.parse(parsedUrl.query);  
  
  const token = queryParams.token;  

  if ( token !== SECRETTOKEN) {
    console.log('InvalidToken:', token);
    socket.destroy();
  }

  if (pathname === WEBSOCKETPATH) {

    wss1.handleUpgrade(request, socket, head, function done(ws) {
      wss1.emit('connection', ws, request);
    });

  } else if (pathname === WEBSOCKETVIDEOPATH) {

    wss2.handleUpgrade(request, socket, head, function done(ws) {
      wss2.emit('connection', ws, request);
    });

  }
  
  else {
    socket.destroy();
  }
});

server.listen({host:"0.0.0.0", port: 8080 });
console.log(`Server started on port 8080! Websocket connection on ${WEBSOCKETPATH}`);

