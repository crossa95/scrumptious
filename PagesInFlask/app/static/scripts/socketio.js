var socket = io();
let room = document.querySelector("#sidebar > p:nth-child(2)").innerHTML;
const username = document.querySelector('#get-username').innerHTML;
const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
document.addEventListener('DOMContentLoaded', () => {    
    joinRoom(room);
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
            span_username.innerText = data['username'];

            //timestamp
            span_timestamp.setAttribute("class", "timestamp")
            span_timestamp.innerText = data['time_stamp'];

            // HTML to append
            p.innerHTML += span_username.outerHTML + br.outerHTML + data['msg'] + br.outerHTML + span_timestamp.outerHTML;
            document.querySelector('#display-message-section').append(p);
        }
         // Display other users' messages
         else if (typeof data.username !== 'undefined') {
            p.setAttribute("class", "others-msg");

            // Username
            span_username.setAttribute("class", "other-username");
            span_username.innerText = data['username'];

            // Timestamp
            span_timestamp.setAttribute("class", "timestamp");
            span_timestamp.innerText = data['time_stamp'];

            // HTML to append
            p.innerHTML += span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;

            //Append
            document.querySelector('#display-message-section').append(p);
        }
        // Display system message


        else {
            printSysMsg(data['msg']);
        }

    });

    // Send message
    document.querySelector('#send_message').onclick = () => {
       
        socket.send({'msg': document.querySelector('#user_message').value,
                    'username': username, 'room': room, 'room_displayed':room, project_id:project_id});
        
        // Clear input area
        document.querySelector('#user_message').value = '';
    }
    navBarSetUp();
    
})

// Leave room
function leaveRoom(room) {
    rooms = document.querySelectorAll('.select-room').forEach(p =>{
        if (p.innerHTML == room){
            if (p.hasAttribute("room_id")){
                socket.emit('leave', {'username': username, 'room': p.getAttribute("room_id"),'display_name':p.innerHTML , project_id:project_id})
            }
            else{
                socket.emit('leave', {'username': username, 'room': room , 'display_name':room,project_id:project_id})
            }
        }
    })
}

// Join room
function joinRoom(room) {
    socket.emit('join', {'username': username, 'room': room, project_id:project_id})
    
    
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

socket.on('cardDragging', data  => {      
    var element = document.getElementById(data);
    element.style.opacity = 0.2;
})

socket.on('cardDrop', data => {       
    var element = document.getElementById(data.id);
    element.style.opacity = 1.0;
    document.getElementById(data.parent).append(element);
    
})

socket.on('cardReset',data => {       
    var element = document.getElementById(data['id']);
    document.querySelector("#backlog_1").append(element);
})

socket.on('cardClick', data => {
    ele_id = data['id'];
    new_text = data['json'];
    new_text = String(new_text);
    var element = document.getElementById(ele_id);
    element.innerText = new_text;
})

socket.on('cardEdit',json => {
    ele_id = "card_"+String(json['card_id']);
    var element = document.getElementById(ele_id);
    console.log(element);
    shown = element.innerText;
    if(shown == json['old_title']){
        element.innerText = json['new_title'];
    }
    else{
        element.innerText = json['new_description'];
    }
})

socket.on('cardDelete', json => {
    ele_id = "card_"+String(json["card_id"]);
    var element = document.getElementById(ele_id);
    element.remove();
})


socket.on('cardPriority', json => {
    ele_id = "card_"+String(json["card_id"])
    var element = document.getElementById(ele_id);
    element.style.color = json['priority'];
})

socket.on('cardCreate', json => {
    const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    if (json['project_id'] == project_id){
        ele_id = "card_"+String(json["card_id"])
        element = document.createElement("div");
        element.classList="list-item";
        element.draggable="true";
        element.id=ele_id;
        element.innerText = json['title'];
        element.setAttribute("priority", json['priority']);
        element.addEventListener('dragstart', function(){
            draggedItem = element;
            setTimeout(function () {
                socket.emit('cardDragStart', element.id);            
            }, 0);
        });

        element.addEventListener('dragend', function () {
            setTimeout(function () {                        
                //draggedItem = null;
            }, 0);
        });
        
        element.addEventListener('click', function() {
            card_id = element.id;
            card_id = parseInt(card_id.replace("card_",""));

            socket.emit('cardClick', {'id':card_id, 'displayed':element.innerText});
        });
        console.log(element)
        document.querySelector("#backlog_1").appendChild(element);
    }
    
})

socket.on('sprintCreate', json => {
    project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    if (json['project_id'] == project_id){
        nav =  document.querySelector("#board > div > ul");
        newSprint = document.createElement("li");
        newSprint.className = "nav-item";
        string1 = '<a class = "nav-link" href="#sprint_"'+json['sprint_id']+' data-toggle="tab" >Sprint '+json['sprint_id']+'</a></li>'
        newSprint.innerHTML = string1;

        if (newSprint.innerText != document.querySelector("#board > div > ul").lastElementChild.previousElementSibling.innerText){
            nav.insertBefore(newSprint,document.querySelector("#board > div > ul").lastElementChild);
            newContent = document.createElement("div");
            newContent.className = "tab-pane";
            newContent.id = "sprint_"+json['sprint_id'];
            string2 = '<div class = "lists">' +
                '<div class = "list" for="In Progress" id=ip_' + json['sprint_id'] + '>' +
                    '<h4 style="text-align:center">In Progress</h4>' +
                '</div>' +
                '<div class = "list" for="Done" id=done_' + json['sprint_id'] + '>' +
                    '<h4 style="text-align:center">Done</h4>' +
                '</div>' +
            '</div>';
            newContent.innerHTML = string2;
            document.querySelector("#board > div > div.tab-content").append(newContent);
            }
            newSprint.addEventListener("click", function () {
                oldactive = document.getElementsByClassName("tab-pane active")[1];
                panes = document.getElementsByClassName("tab-pane");
                newactive = panes.namedItem("sprint_"+json['sprint_id']);
                oldactive.className = "tab-pane";
                newactive.className = "tab-pane active";

            });
        }
        $(".nav-tabs").on("click", "a", function (e) {
            e.preventDefault();
            if (!$(this).hasClass('add-contact')) {
                $(this).tab('show');
            }
        })
        .on("click", "span", function () {
            var anchor = $(this).siblings('a');
            $(anchor.attr('href')).remove();
            $(this).parent().remove();
            $(".nav-tabs li").children('a').first().click();

        });
        
        const list_items = document.querySelectorAll('.list-item');
        const lists = document.querySelectorAll('.list');

        let draggedItem = null;
        for (let i = 0; i<list_items.length; i++){
            const item = list_items[i];

            item.addEventListener('dragstart', function(){
                draggedItem = item;
                setTimeout(function () {
                    socket.emit('cardDragStart', item.id);            
                }, 0);
            });

            item.addEventListener('dragend', function () {
                setTimeout(function () {                        
                    //draggedItem = null;
                }, 0);
            });
            
            item.addEventListener('click', function() {
                card_id = item.id;
                card_id = parseInt(card_id.replace("card_",""));

                socket.emit('cardClick', {'id':card_id, 'displayed':item.innerText});
            });

            for (let j = 0; j < lists.length; j++){
                const list = lists[j];
                list.addEventListener('dragover', function (e) {
                    e.preventDefault();
                });
                list.addEventListener('dragenter', function (e) {
                    e.preventDefault();
                    this.style.backgroundColor = '#d2d6d6';
                });
                list.addEventListener('dragleave', function (e){
                    this.style.backgroundColor = '#eaeded';
                });
                list.addEventListener('drop', function (e) {
                    let element = this;          
                    let newSprint = element.id.split("_"); /* default to the backlog */
                    let status = 'backlog';
                    let stReg = /ip/;
                    if(stReg.test(element.id)){
                        status = 'incomplete';   /* Reg expressions to identify the new status */
                    }
                    stReg = /done/;
                    if(stReg.test(element.id)){
                        status = 'complete';
                    }
                    this.append(draggedItem);
                    this.style.backgroundColor = '#eaeded';
                    socket.emit('cardDrop', { 'id': draggedItem.id, 'parent':element.id,
                    'status':status, "newSprint": newSprint[1]});
                });
            }
        }
    });

socket.on('deleteSprint', json =>{
    const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    if(json['project_id'] == project_id){
        $( "a" ).each(function() {
            if(this.innerText == json['id']){
                if (this.className == "nav-link active"){
                    this.parentElement.remove();
                    this.remove();
                    if (json['id'] == "Sprint 1"){
                        $( "a" ).each(function(){
                            if(this.innerText.includes("Sprint 2")){
                                this.click();
                            }
                        })
                    }
                    else{
                        $( "a" ).each(function(){
                            if(this.innerText.includes("Sprint 1")){
                                this.click();
                            }
                        })
                    }
                }
                else{
                    this.parentElement.remove();
                    this.remove();
                }
                
            }
          });
        
        
    }
});

socket.on('sprintDecrement', json =>{
    const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    console.log(json["id"])
    console.log(json['new_id'])
    if(json['project_id'] == project_id){
        $( "a" ).each(function() {
            if(this.innerText == json['id']){
                this.innerText = json['new_id'] 
            }
          });
    }
})

function getData(){
        newtitle = document.querySelector("#myForm > textarea").value;
        newdescription = document.querySelector("#myForm > textarea:nth-child(4)").value;
        document.getElementById("myForm").style.display = "none";
        card_id = document.getElementById("myForm").card;
        socket.emit('cardEdit',{'new_title':newtitle,'new_description':newdescription,'card_id':card_id});
}

function openForm() {
        document.getElementById("myForm").style.display = "block";
}

function closeForm() {
        document.getElementById("myForm").style.display = "none";
}
/**
   * Actions For Each ContextMenu Option
   */
function menuItemListener( link ) {
    //project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    
    if (link.getAttribute('data-action') == 'Edit'){
        card_id = CardInContext.id;
        card_id = parseInt(card_id.replace("card_",""));
        socket.emit('cardInfo',{'card_id':card_id});
        socket.on('cardInfo', json=>{
            card_desc = json['description'];
            card_title = json['title'];
            console.log(card_desc)
            console.log(card_title)
            document.querySelector("#myForm > textarea").value = card_title;
            document.querySelector("#myForm > textarea:nth-child(4)").value = card_desc;
            document.getElementById("myForm").card = json['card_id'];
            positionX = CardInContext.getBoundingClientRect().right;
            positionY = CardInContext.getBoundingClientRect().y;
            console.log(CardInContext)
            $('.card-popup').css("left" , String(positionX-100)+"px");
            $('.card-popup').css("top" , String(positionY-150)+"px");

            openForm();
        });
        
    }
    else if (link.getAttribute('data-action') == 'Delete'){
        card_id = CardInContext.id;
        card_id = parseInt(card_id.replace("card_",""));
        console.log(card_id)
        socket.emit('cardDelete', {'card_id':card_id});
    }
    else if(link.getAttribute('data-action') == 'Set Priority'){
        console.log("here")
        card_id = CardInContext.id;
        card_id = parseInt(card_id.replace("card_",""));
        console.log(card_id)
        socket.emit('cardPriority', {'card_id':card_id});
    }
    else if(link.getAttribute('data-action')=='Delete Sprint'){
        sprintNum = SprintInContext.innerText.replace("Sprint ","");
        numSprints = $(".nav-tabs").children().length - 1;
        if (numSprints != 1){
            console.log("emitted sprintDelete")
            const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
            socket.emit('sprintDelete',{'project_id':project_id,'numSprints':numSprints,'sprintNum':sprintNum})
        }
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

var CardItemClassName = "list-item";
var CardInContext;

    
var SprintItemClassName = "nav-link";
var SprintInContext;

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
      CardInContext = clickInsideElement( e, CardItemClassName );
      SprintInContext = clickInsideElement(e,SprintItemClassName);
      if ( CardInContext ) {
        positionX = CardInContext.getBoundingClientRect().right;
        positionY = CardInContext.getBoundingClientRect().y;
        e.preventDefault();
        toggleMenuOn();
        positionMenu(positionX,positionY);
      }
      else if (SprintInContext){
        if (SprintInContext.text.includes("Sprint ")){
            console.log(SprintInContext)
            e.preventDefault();
            SprintInContext.click();
            toggleSprintPopMenuOn();
        }
      }
      else {
        CardInContext = null;
        SprintInContext = null;
        toggleMenuOff();
        toggleSprintPopMenuOff();
      }
    });
}

function clickListener() {
    document.addEventListener( "click", function(e) {
        var clickeElIsLink = clickInsideElement( e, contextMenuLinkClassName );
        var clickEIsPopUp = clickInsideElement(e,"card-popup");
        var clickEIsChannelPop = clickInsideElement(e,"channel-popup");
        var clickEIsAddChannel = clickInsideElement(e,"add-room");
        if ( clickeElIsLink ) {
            e.preventDefault();
            menuItemListener( clickeElIsLink );
        } 
        else if (clickEIsPopUp){
            // do nothing
        }
        else if (clickEIsChannelPop){
            // do nothing
        }
        else if (clickEIsAddChannel && document.getElementById("channel-popup").style.display == "none"){
           getMembers();
        }
        else {
            var button = e.which || e.button;
            if ( button === 1 ) {
            toggleMenuOff();
            toggleChannelPopUpOff();
            toggleSprintPopMenuOff();
            closeForm();
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
  
function positionMenu(x,y) { 
    menu.style.left = String(x)+"px";
    menu.style.top = String(y-100)+"px";
}
  
function toggleSprintPopMenuOn(){
    document.getElementById("sprint-pop").style.display = "block";
}
function toggleSprintPopMenuOff(){
    document.getElementById("sprint-pop").style.display = "none";
}

function getMembers(){
    const username = document.querySelector('#get-username').innerHTML;
    const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    toggleChannelPopUpOn();
    socket.emit('getMembers',{'username':username,'project_id':project_id})
}

socket.on('buildNewChannel', json=>{
    //project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    if (json['project_id'] == project_id){
        popup = document.querySelector("#members-options > ul");
        newUser = document.createElement("div");
        newUser.className = "listofusers"

        img = document.createElement("img");
        img.className = "avatar";
        img.setAttribute("src",'/static/profile_pics/'+json['image_file']);
        img.setAttribute("alt","user_image");

        checkbox = document.createElement('input');
        checkbox.setAttribute("type","checkbox");
        checkbox.setAttribute("id",json['user_id']);
        checkbox.className = "checkNames";

        newUser.appendChild(img);
        newUser.append(json['username']);
        newUser.appendChild(checkbox);
        
        popup.appendChild(newUser);
    }
})

function toggleChannelPopUpOn(){
    document.getElementById("channel-popup").style.display = "block";
}

function toggleChannelPopUpOff(){
    document.getElementById("channel-popup").style.display = "none";
    popup = document.querySelector("#members-options > ul").innerHTML = "";
    document.querySelector("#channel-popup > input").value = "";
}

function makeChannel(){
    const username = document.querySelector('#get-username').innerHTML;
    const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    name = document.querySelector("#channel-popup > input").value;
    numusers = $('.checkNames:checkbox:checked').length+1;
    console.log(numusers)
    if (numusers == 1){
        toggleChannelPopUpOff();
    }
    else if(numusers == 2){
        checkedUserID = $('.checkNames:checkbox:checked')[0].id;
        console.log(checkedUserID)
        socket.emit('createDirectMessagingRoom',{'project_id':project_id,'username':username,'otheruser_id':parseInt(checkedUserID)})
        toggleChannelPopUpOff();
    }
    else{
        if (name.trim() == ""){
            alert("Channel Name is required for Group Channels")
        }
        else{
        users = []
        checkedUsers = $('.checkNames:checkbox:checked').each(function(){
            checkedUserID = this.id;
            users.push(checkedUserID);
        })
        console.log(users)
        socket.emit('createGroupMessagingRoom', {"project_id":project_id,'username':username,'users':users,'roomName':name})
        toggleChannelPopUpOff();
        }  
    }
}

socket.on('displayNewGroupRoom', json=> {
    const username = document.querySelector('#get-username').innerHTML;
    const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);

    var arrayUsers = json['username_list'].split(":");
    console.log(arrayUsers)
    console.log(arrayUsers.includes(username))
    if (arrayUsers.includes(username) && project_id == json['project_id']){
        sidebar = document.querySelector("#sidebar");

        newChannel = document.createElement("p");
        newChannel.className = "select-room";
        newChannel.innerHTML = json['room_title'];

        eles = document.querySelectorAll("#sidebar > p");
            duplicate = false;
            for (let i = 0; i<eles.length; i++){
                if (eles[i].innerHTML == json['room_title']){
                    duplicate = true;
                }
            }
        if(!duplicate){sidebar.insertBefore(newChannel,document.querySelector("#sidebar > button"));}
        navBarSetUp();
    }
})


socket.on('displayNewDMRoom', json=> {
    //const username = document.querySelector('#get-username').innerHTML;
    const project_id = parseInt(document.querySelector('#get-project_id').innerHTML);
    usernames = json['username_list'].split(":");
    if(usernames.includes(username)){
        if (usernames[0] == username){
            room_title = usernames[1];
        }else{
            room_title = usernames[0];
        }
        if (project_id == json['project_id']){
            sidebar = document.querySelector("#sidebar");

            newChannel = document.createElement("p");
            newChannel.className = "select-room";
            newChannel.setAttribute("room_id",json['room_id']);
            newChannel.innerHTML = room_title;
            eles = document.querySelectorAll("#sidebar > p");
            duplicate = false;
            for (let i = 0; i<eles.length; i++){
                if (eles[i].getAttribute("room_id") == json['room_id']){
                    duplicate = true;
                }
            }
            if(!duplicate){sidebar.insertBefore(newChannel,document.querySelector("#sidebar > button"));}
            navBarSetUp();
        }
    }

})
function navBarSetUp(){
    document.querySelectorAll('.select-room').forEach(p => {
        p.onclick = () => {
            if (p.hasAttribute("room_id")){
                let newRoom = p.getAttribute("room_id");
                if (newRoom == room) {
                msg = `You are already in this room.`
                printSysMsg(msg);
                } else {
                    console.log("i made it")
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
                }
            }
            else{let newRoom = p.innerHTML;
                if (newRoom == room) {
                    msg = `You are already in this room.`
                    printSysMsg(msg);
                } else {
                    leaveRoom(room);
                    joinRoom(newRoom);
                    room = newRoom;
                }
            }    
        }
    });
}
    
socket.on('listInvitedUser', json =>{
    if (json['project_id'] == project_id && json['username'] != username && json['new_member_username'] != username){
        new_username = json['new_member_username'];
        new_photo = json['new_member_photo'];

        memlist = document.querySelector("#members");
        newUser = document.createElement("ul");
        newListItem = document.createElement("li");

        img = document.createElement("img");
        img.className = "avatar";
        img.setAttribute("src",'/static/profile_pics/'+new_photo);
        img.setAttribute("alt","user_image");

        newListItem.appendChild(img);
        newListItem.append(" "+new_username);
        newUser.appendChild(newListItem);
        
        memlist.insertBefore(newUser,document.querySelector("#members > a"));

    }
})

init();