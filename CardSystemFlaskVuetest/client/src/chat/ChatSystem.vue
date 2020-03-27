<template>
  <div class="chatSystem">
    <h2>This is where the chat system will be!</h2>
    <tabs : mode = "mode">
      <tab title="Chat">
        <Chat/>
      </tab>
    </tabs>
  </div>
</template>

<script>
  import Tab from '@/components/Chat.vue'
/* eslint-disable */
export default {
  name: 'ChatSystem',
  props: {
    msg: String
  },
  components:{
    Chat
  }
}
</script>

<style scoped>
  h2{
    margin-top: 0 auto;
  }
</style>
