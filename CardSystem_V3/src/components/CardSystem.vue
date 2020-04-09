<template>
<div class="Wrapper">

<div class="Backlog">
          <BackLog />
</div>
<div class="cardSystem">
    <b-card no-body>
      <b-tabs card>

        <b-tab title="Trash">
          <Trash />
        </b-tab>

        <b-tab title="Sprint 1">
          <Sprints />
        </b-tab>
        
        <b-tab v-for="i in tabs" :key="'dyn-tab-' + i" :title="'Sprint ' + i">
          <b-button size="sm" variant="danger" class="float-right" @click="closeTab(i)">
            Close Tab
          </b-button>
          <Sprints />
        </b-tab>

        <template v-slot:tabs-end>
          <b-nav-item @click.prevent="newTab" href="#"><b>+</b></b-nav-item>
        </template>
      </b-tabs>
      
    </b-card>
  </div>
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
  .Backlog {
    width: 30%;
    min-height: 100vh;
    background-color: #f8f8f8;
    margin: 10px;
    padding: 20px;
    float:left;
  }
  .cardSystem {
    width: 65%;
    min-height: 100vh;
    background-color: #f8f8f8;
    margin: 10px;
    padding: 20px;
    float:right;
  }

</style>