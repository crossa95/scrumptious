
/**
 * Code from simple a private messaging flask socketio 
 * 
 * Using it to help problem solve the Tab ID problem
 * They used a user list (with a corresponding session id)
 * 
 

$(document).ready(function() {

    var private_socket = io('http://127.0.0.1:5000/private')

    $('#send_username').on('click', function() {
        private_socket.emit('username', $('#username').val());
    });

    $('#send_private_message').on('click', function() {
        var recipient = $('#send_to_username').val();
        var message_to_send = $('#private_message').val();
        private_socket.emit('private_message', {'username' : recipient, 'message' : message_to_send});
    });

    private_socket.on('new_private_message', function(msg) {
        alert(msg);
    });

    /*
    socket.on('connect', function() {
        socket.send('I am now connected!');
        socket.emit('custom event', {'name' : 'Anthony'});
        socket.on('from flask', function(msg) {
            alert(msg['extension']);
        });
        socket.on('message', function(msg) {
            alert(msg);
        });
    });

});

* //*/
