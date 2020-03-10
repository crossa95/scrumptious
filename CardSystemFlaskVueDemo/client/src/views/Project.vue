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
      <ChatSystem />
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
      currentTab: 1
    }
  },
  methods:{
    selectTab(selectedTab){
      this.currentTab = selectedTab
    }
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
