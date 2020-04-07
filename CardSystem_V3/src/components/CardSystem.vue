<template>
  <div class="cardSystem">
    <b-card no-body>
      <b-tabs card>
        <b-tab title="Backlog">
          <BackLog details="This is the BackLog"/>
        </b-tab>
        <b-tab title="Trash">
          <Trash trash="This is the Trash"/>
        </b-tab>
        <b-tab title="Sprint 1">
          <Sprints todo="The ToDo Column" inprogress="The In-Progress Column" done="The Done Column"/>
        </b-tab>
        <b-tab v-for="i in tabs" :key="'dyn-tab-' + i" :title="'Sprint ' + i">
          <b-button size="sm" variant="danger" class="float-right" @click="closeTab(i)">
            Delete Tab
          </b-button>
          <Sprints />
        </b-tab>
        <template v-slot:tabs-end>
          <b-nav-item @click.prevent="newTab" href="#"><b>+</b></b-nav-item>
        </template>
      </b-tabs>
    </b-card>
  </div>
</template>

<script>
import BackLog from '@/components/BackLog';
import Sprints from '@/components/Sprints';
import Trash from '@/components/Trash';

export default {
  name: 'CardSystem',
  props: {
    msg: String
  },
  components:{
    BackLog,
    Sprints,
    Trash
    
  },
  data () {
    return {
      tabs:[],
      tabCounter:2
    }
  },
  methods: {
    newTab(){
      this.tabs.push(this.tabCounter++);
    },
    closeTab(x){
      for(let i=0; i<this.tabs.length; i++)
      {
        if(this.tabs[i]===x){
          this.tabs.splice(i,1)
        }
      }
      this.tabCounter = x;
    }    
  }
}
</script>

<style lang="css">
  * {
    margin: 0;
    padding: 0;
    font-family: 'Karla', sans-serif;
  }
  .cardSystem {
    width: 100%;
    min-height: 100vh;
    background-color: #f8f8f8;
    margin: 10px;
    padding: 20px;
  }

</style>