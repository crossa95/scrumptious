<template>
  <div class="manage">
    <img alt="Vue logo" src="../assets/logo.png">
    <h1>Project Manager</h1>
    <p>
        This is where the user can create a new project, manage the projects they already have, and choose the project they would like to go into.
    </p>
    <div class="recent">
      <h3>Most Recent</h3>
      <button>
        <router-link to="/project">Project 1</router-link>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Manage',
  components: {
    
  }
}
</script>
<style scoped>
  .manage{
    text-align: center;
  }
  .recent{
    text-align: left;
  }
  button{
  background-color: #D3D3D3;
  color: #000000;
  font-style: bold;
  padding: 5px 10px;
  margin-right: 8px;
  border: 0px;
  border-radius: 100px;
  cursor: pointer;
}
</style>