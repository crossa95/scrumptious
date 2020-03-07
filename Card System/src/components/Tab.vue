<template>
    <div>
      <button @click="selectTab(1)" :class="{'buttonClick' : currentTab ==1}">
        Backlog
      </button>

      <button @click="selectTab(2)" :class="{'buttonClick' : currentTab ==2}">
        Sprint 1
      </button>

      <button @click="selectTab(3)" :class="{'buttonClick' : currentTab ==3}">
        Trash
      </button>

      <div v-if="currentTab == 1">
        <h3>BackLog</h3>
        <p>
          The Backlog is where the users will be able to create cards and have the store until they are ready to be added to a Sprint!
        </p>
        <BackLog />
      </div>

      <div v-if="currentTab == 2">
        <h3>Sprint 1</h3>
        <p>
          The user will be able to drag cards into the Sprint and can organize them into three groups: To-Do, In-Progress, and Done!
        </p>
        <Sprints />
      </div>

      <div v-if="currentTab == 3">
        <h3>Trash</h3>
        <p>
          The user can throw out cards here, but still have them easily available should they decide that they wanted that card afterall!
        </p>
        <Trash />
      </div>

    </div>
</template>
<script>
import BackLog from '@/components/BackLog';
import Sprints from '@/components/Sprints';
import Trash from '@/components/Trash';
export default {
  name: 'Tab',
  props:{

  },
  components:{
    BackLog,
    Sprints,
    Trash
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
button{
  background-color: #566;
  color: white;
  font-style: bold;
  padding: 5px 10px;
  margin-right: 8px;
  border: 0px;
  border-radius: 100px;
  cursor: pointer;
}

.buttonClick{
  background: #000;
}
</style>
