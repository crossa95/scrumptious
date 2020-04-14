var socket = io();
document.addEventListener('DOMContentLoaded', () => {    

    // retrive username
    const username = document.querySelector('#get-username').innerHTML;

    //set default room
    let room = "General";
    joinRoom("General");

    // Displays incoming messages
    socket.on('message', data => {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const br = document.createElement('br');

        if (data.username == username){
            p.setAttribute("class", "my-msg");

            //username
            span_username.setAttribute("class", "my-username")
            span_username.innerText = data.username;

            //timestamp
            span_timestamp.setAttribute("class", "timestamp")
            span_timestamp.innerText = data.time_stamp;

            // HTML to append
            p.innerHTML += span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;
            document.querySelector('#display-message-section').append(p);
        }
         // Display other users' messages
         else if (typeof data.username !== 'undefined') {
            p.setAttribute("class", "others-msg");

            // Username
            span_username.setAttribute("class", "other-username");
            span_username.innerText = data.username;

            // Timestamp
            span_timestamp.setAttribute("class", "timestamp");
            span_timestamp.innerText = data.time_stamp;

            // HTML to append
            p.innerHTML += span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;

            //Append
            document.querySelector('#display-message-section').append(p);
        }
        // Display system message


        else {
            printSysMsg(data.msg);
        }

    });

    // Send message
    document.querySelector('#send_message').onclick = () => {
        socket.send({'msg': document.querySelector('#user_message').value,
            'username': username, 'room': room });

        // Clear input area
        document.querySelector('#user_message').value = '';
    }

    document.querySelectorAll('.select-room').forEach(p => {
        p.onclick = () => {
            let newRoom = p.innerHTML;
            if (newRoom == room) {
                msg = `You are already in ${room} room.`
                printSysMsg(msg);
            } else {
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
            }
        }
    });

    // Leave room
    function leaveRoom(room) {
        socket.emit('leave', {'username': username, 'room': room});
    }

    // Join room
    function joinRoom(room) {
        socket.emit('join', {'username': username, 'room': room})

        // Clear message area
        //document.querySelector('#display-message-section').innerHTML = ''

        //autofocus on textbox
        document.querySelector('#user_message').focus()


    }

    // Print System Message

    function printSysMsg(msg) {
        const p = document.createElement('p');
        p.innerHTML = msg;
        document.querySelector('#display-message-section').append(p);
    }

    /* socket.on('cardDragStart', data => {
        id = data;        
    }) */

})

socket.on('cardDragging', data  => {        
    var element = document.getElementById(data);
    element.style.opacity = 0.2;
})

socket.on('cardDrop', data => {        
    var element = document.getElementById(data.id);
    element.style.opacity = 1.0;
    document.getElementById(data.parent).append(element);
    
})