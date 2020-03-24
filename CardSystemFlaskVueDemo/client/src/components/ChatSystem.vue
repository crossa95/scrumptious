<template>
  <div class="chatSystem">
    <ChatTabs>
      <ChatTab v-for="tab in chatTabs" :key='tab.id' :chatID='tab.id' :title="tab.title"
                :messages="messages"
                @newMsg = "passMsg($event)">
      </ChatTab>
    </ChatTabs>
  </div>
</template>

<script>
import ChatBox from '@/components/ChatBox.vue'
import ChatTabs from '@/components/ChatTabs.vue'
import ChatTab from '@/components/ChatTab.vue'
//  import io from 'socket.io-client'
/* eslint-disable */
export default {
  name: 'ChatSystem',
  props: {
   messages: Array,
   chatTabs: Array
  },
  data () {
    return{

    }
  },
  components:{
    ChatBox,
    ChatTabs,
    ChatTab
  },
  created (){
    
  },
  methods: {
    passMsg(msg){      
      this.$emit('newMsg', msg);
    }
  }
}
</script>