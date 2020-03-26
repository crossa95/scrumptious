<template>
    <div id="chat">
        <ul id="chatbox">
            <ChatMessage
                v-for = "message in filterMessages"
                :key = "message.id"
                :message = "message"
            ></ChatMessage>
        </ul>
        <form @submit.prevent="sendMessage">
            <label id="inputLabel"> Message: </label>
            <input type="text" placeholder="Message..." v-model="message" />
           <input type="submit" value="Send" />
        </form>
    </div>
</template>
<script>
// import io from 'socket.io-client'
import ChatMessage from '@/components/ChatMessage.vue'

/* eslint-disable */
export default { 
    components:{
        ChatMessage
    },
    props:{
        messages: Array,
        chatID: Number
    },
    data () {
        return {                            
            message: '',
            //messages: ['Hello','How are you'],
        }
    },
        methods: {
            sendMessage: function () {          
                this.$emit("newMsg", {channel: this.chatID, content: this.message});               
                this.message = '';
            }
        },
        computed: {
            filterMessages() {
                let chatID = this.chatID;
                let messages = this.messages;
                let newArray = messages.filter(function (message) {
                    return message.channel == chatID;
                })
                return newArray;
            }
        }
    };
</script>

<style scoped>
#chatbox {
    height: 300px;
    width: 500px;
    background-color: rgb(212, 243, 247);
    overflow: auto;
    border-radius: 25px;
    border-style:inset;
    border-width: 2px;
    border-color: rgb(64, 75, 77);
    padding-top: 5px;
}
::-webkit-scrollbar{
    width: 20px;
}
::-webkit-scrollbar-track-piece{
    background: rgb(21, 40, 43);
    border-top-right-radius: 25px;
    border-bottom-right-radius: 25px;
}
::-webkit-scrollbar-thumb{
    background: rgb(112, 123, 124);
    border-top-right-radius: 25px;
    border-bottom-right-radius: 25px;     
}
::-webkit-scrollbar-thumb:hover {
    background: rgb(64, 75, 77);
}
#inputLabel {
    padding-left: 25px;
}
</style>
