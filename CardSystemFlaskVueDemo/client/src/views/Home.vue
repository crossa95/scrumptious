<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <h1>Welcome to PMT!</h1>
    <h1>What is it?</h1>
    <p>
      Scrumptious is a web app used for communication and work organization during various projects. It utilizes Vue.js to build the front end while the backend is handled by Flask. 
    </p>
    <h1>Why use it?</h1>
    <p>
      Scrumptious has a chat function for communications and a kanban board for organizing the team on what they're currently meant to do. Both of these functions are also tied to thier own project and allow for multiple chats pertaining to a specific project to be active. This also grants a very organized and convenient way to manage multiple projects going on at the same time. 
    </p>
  </div>
</template>

<script>
/* eslint-disable */
export default {
  name: 'Home',
  components: {
    
  }
}
</script>
<style scoped>
  .home{
    text-align: center;
  }
</style>
