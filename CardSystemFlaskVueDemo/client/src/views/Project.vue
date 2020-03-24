<template>
  <div class="project">
    <h1>Project</h1>
    <button @click="selectTab(1)" :class="{'buttonClick' : currentTab ==1}">
      Chat
    </button>
    <button @click="selectTab(2)" :class="{'buttonClick' : currentTab ==2}">
      Card Board
    </button>
    <div v-if="currentTab == 1">
      <keep-alive>
      <ChatSystem :messages="messages" :chatTabs="chatTabs" @newMsg = "addMsg($event)" />
      </keep-alive>
    </div>
    <div v-if="currentTab == 2">
      <CardSystem msg="Card Board"/>
    </div>
  </div>
</template>
<script>
/* eslint-disable */
import CardSystem from '@/components/CardSystem.vue'
import ChatSystem from '@/components/ChatSystem.vue'
import io from  'socket.io-client'
export default {
  name: 'Project',
  props:{

  },
  components: {
    CardSystem,
    ChatSystem
  },  
  data: function(){ 
    return{
      socket: {},
      currentTab: 1,
      messages: [{channel: 1, content: 'Hello'}, {channel: 2, content:'How are you?'}, {channel: 3, content:'Nice job!'}],
      chatTabs: [{id: 1, title: 'Team'}, 
                  {id: 2,title:'Jennifer'}, 
                  {id: 3, title:'Joe'}]
    }
  },
  created () {
      this.socket = io('http://localhost:3000/chat');
      },
  methods:{
    selectTab(selectedTab){
      this.currentTab = selectedTab
    },
    addMsg(msg){
      this.socket.emit("message", msg);
    }
  },
  mounted () {
    this.socket.on("message", msg =>  {
        this.messages.push(msg);
      })
  }
}
</script>
<style scoped>
  h1{
      margin-top: 0 auto;
  }
  button{
    background-color: #566;
    color: white;
    font-style: bold;
    padding: 15px 20px;
    margin-right: 8px;
    margin-bottom: 15px;
    border: 0px;
    border-radius: 100px;
    cursor: pointer;
  }
  .buttonClick{
    background: #000;
  }
</style>
