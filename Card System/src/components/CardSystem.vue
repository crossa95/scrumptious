<template>
  <div class="cardSystem">
    <h2>{{ msg }}</h2>
    <Tab />
  </div>
</template>

<script>
import Tab from '@/components/Tab.vue'
export default {
  name: 'CardSystem',
  props: {
    msg: String
  },
  components:{
    Tab
  }
}
</script>

<style scoped>
  h2{
    margin-top: 0 auto;
  }
</style>
