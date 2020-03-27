<template>
  <div class="sprints">
    <main class="flexbox">
      <Board id = "board-1">
        <h1 style="color: white; font-size:30px; text-align: center">TO DO</h1>
        <Card id = "card-1" draggable = "true">
          <p> Card One </p>
        </Card>
      </Board>
      <Board id = "board-2">
        <h1 style="color: white; font-size:30px; text-align: center">IN PROGRESS</h1>
        <Card id = "card-2" draggable = "true">
          <p> Card Two </p>
        </Card>
      </Board>
      <Board id = "board-3">
        <h1 style="color: white; font-size:30px; text-align: center">DONE</h1>
        <Card id = "card-3" draggable = "true">
          <p> Card Three </p>
        </Card>
      </Board>
    </main>
  </div>
</template>

<script>
/* eslint-disable */
import Board from '@/components/Board';
import Card from '@/components/Card';
export default {
  name: 'Sprint',
  props: {

  },
  components:{
    Board,
    Card
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  background-color: #F3F3F3
}
.flexbox {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 1000px;
  height: 100vh;
  overflow: hidden;
  margin: 0 auto;
  padding: 15px;
}
.flexbox .board {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 300px;
  background-color: #313131;
  padding: 15px;
}
.flexbox .board .card {
  padding: 15px 25px;
  background-color: #F3F3F3;
  cursor: pointer;
  margin-bottom: 15px
}
</style>
