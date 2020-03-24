<template lang="html">
  <div class='chat-tab' v-show='isActive'>
    <ChatBox  :messages="messages" :chatID="chatID" @newMsg="passMsg($event)"></ChatBox>
  </div>
</template>

<script>
/* eslint-disable */
import ChatBox from '@/components/ChatBox.vue'
export default {
    components:{
        ChatBox
    },
  props: {
    title: {
      type: String,
      default: 'Tab'
    },
    messages: Array,
    chatID: Number
  },
  data () {
    return {
      isActive: true
        }
    },
    methods: {
        passMsg(msg){
        this.$emit('newMsg', msg);
        }
    }
  }

</script>

<style lang="css">
  
</style>