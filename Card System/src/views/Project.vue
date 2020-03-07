<template>
    <div class="project">
        <h1>Project</h1>
        <CardSystem msg="Card Board"/>
    </div>
</template>
<script>
import CardSystem from '@/components/CardSystem.vue'
export default {
  name: 'Project',
  components: {
    CardSystem
  }
}
</script>
<style scoped>
    h1{
        margin-top: 0 auto;
    }
</style>