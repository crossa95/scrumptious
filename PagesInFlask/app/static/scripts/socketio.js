var socket = io();
document.addEventListener('DOMContentLoaded', () => {    

    // retrive username
    const username = document.querySelector('#get-username').innerHTML;
    const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
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
            'username': username, 'room': room , project_id:project_id});

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
        socket.emit('join', {'username': username, 'room': room , project_id:project_id})

        // Clear message area
        document.querySelector('#display-message-section').innerHTML = ''

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

socket.on('cardClick', data => {
    ele_id = data['id'];
    new_text = data['json'];
    new_text = String(new_text);
    var element = document.getElementById(ele_id);
    element.innerText = new_text;
})

socket.on('cardDelete', json => {
    ele_id = "card_"+String(json["card_id"])
    var element = document.getElementById(ele_id);
    console.log(element)
    element.remove();
})


socket.on('cardPriority', json => {
    ele_id = "card_"+String(json["card_id"])
    var element = document.getElementById(ele_id);
    console.log(element)
    element.style.color = json['priority'];
})
/**
   * Actions For Each ContextMenu Option
   */
  function menuItemListener( link ) {
    console.log( "Card ID - " + CardInContext.getAttribute("data-id") + ", Card action - " + link.getAttribute("data-action"));
    console.log(CardInContext)
    project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    username = document.querySelector('#get-username').innerHTML;
    if (link.getAttribute('data-action') == 'Edit'){
        
        CardInContext.addAttribute
        
        
        card_id = CardInContext.id;
        card_id = parseInt(card_id.replace("card_",""));
        console.log(card_id)
        socket.emit('cardEdit', project_id,username,card_id);
    }
    else if (link.getAttribute('data-action') == 'Delete'){
        card_id = CardInContext.id;
        card_id = parseInt(card_id.replace("card_",""));
        console.log(card_id)
        socket.emit('cardDelete', {'card_id':card_id});
    }
    else if(link.getAttribute('data-action') == 'Set Priority'){
        card_id = CardInContext.id;
        card_id = parseInt(card_id.replace("card_",""));
        console.log(card_id)
        socket.emit('cardPriority', {'card_id':card_id});
    }
    else{}
    
    toggleMenuOff();
  }


// Context Menu Setup Below
function clickInsideElement( e, className ) {
    var el = e.srcElement || e.target;
    
    if ( el.classList.contains(className) ) {
      return el;
    } else {
      while ( el = el.parentNode ) {
        if ( el.classList && el.classList.contains(className) ) {
          return el;
        }
      }
    }

    return false;
  }

  var contextMenuLinkClassName = "context-menu__link";
  var contextMenuActive = "context-menu--active";

  var taskItemClassName = "list-item";
  var CardInContext;

  var menu = document.querySelector("#context-menu");
  var menuItems = menu.querySelectorAll(".context-menu__item");
  var menuState = 0;

  function init() {
    contextListener();
    clickListener();
    keyupListener();
    resizeListener();
  }

  /**
   * Listens for contextmenu events.
   */
  function contextListener() {
    document.addEventListener( "contextmenu", function(e) {
      CardInContext = clickInsideElement( e, taskItemClassName );

      if ( CardInContext ) {
        e.preventDefault();
        toggleMenuOn();
        positionMenu(e);
      } else {
        CardInContext = null;
        toggleMenuOff();
      }
    });
  }

  function clickListener() {
    document.addEventListener( "click", function(e) {
      var clickeElIsLink = clickInsideElement( e, contextMenuLinkClassName );

      if ( clickeElIsLink ) {
        e.preventDefault();
        menuItemListener( clickeElIsLink );
      } else {
        var button = e.which || e.button;
        if ( button === 1 ) {
          toggleMenuOff();
        }
      }
    });
  }

  function keyupListener() {
    window.onkeyup = function(e) {
      if ( e.keyCode === 27 ) {
        toggleMenuOff();
      }
    }
  }
  function resizeListener() {
    window.onresize = function(e) {
      toggleMenuOff();
    };
  }

  function toggleMenuOn() {
    if ( menuState !== 1 ) {
      menuState = 1;
      menu.classList.add( contextMenuActive );
    }
  }

  function toggleMenuOff() {
    if ( menuState !== 0 ) {
      menuState = 0;
      menu.classList.remove( contextMenuActive );
    }
  }

  function positionMenu(e) {
    menu.style.left = "485px";
    menu.style.top = "435px";
  }

  init();