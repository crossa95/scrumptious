<template>
  <div id="app">
    <div id="nav">
      <router-link to="/manage">Project Manager</router-link> |
      <router-link to="/user">User</router-link> |
      <router-link to="/about">About</router-link>
      <router-link to="/home">Home</router-link>
    </div>
    <router-view />
  </div>
</template>
<script>
/* eslint-disable */
export default {
  name: 'App'
}
</script>
<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
}
#nav {
  text-align: right;
  font-size: 12px;
  padding: 30px;
}
#nav a {
  font-weight: bold;
  color: #2c3e50;
}
#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
