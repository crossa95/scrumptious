const Express = require("express")();
const Http = require("http").Server(Express);
const Socketio = require("socket.io")(Http);

const nsp = Socketio.of('/chat');


nsp.on("connection", socket => {
    socket.on("message", msg => {
        nsp.emit("message", msg);
    });
    console.log("namespace");
});

Socketio.on("connection", socket => {
    socket.on("message", msg => {        
        Socketio.emit("message", msg);
    });
    console.log("a user connected");
});

Http.listen(3000, () => {
    console.log("Listening at :3000...");
});
