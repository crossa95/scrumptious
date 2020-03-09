<template>
  <div class='cardSystem'>
    <tabs :mode="mode">
      <tab title="BackLog">
        <BackLog/>
      </tab>
      <tab title="Trash">
        <Trash />
      </tab>
      <tab title="Sprint 1">
        <Sprints/>
      </tab>
    </tabs>
  </div>
</template>

<script>
import Tab from '@/components/Tab.vue'
import Tabs from '@/components/Tabs.vue'
import BackLog from '@/components/BackLog';
import Sprints from '@/components/Sprints';
import Trash from '@/components/Trash';

export default {
  name: 'CardSystem',
  props: {
    msg: String
  },
  components:{
    Tab,
    Tabs,
    BackLog,
    Sprints,
    Trash
    
  },
  data () {
    return {
      mode: 'light'
    }
  },
  methods: {
    
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
    margin: 0;
    padding: 20px;
  }

  .change__style {
    background-color: #eee;
    font-size: 1em;
    margin-bottom: 10px;
    padding: 5px;
  }
</style>