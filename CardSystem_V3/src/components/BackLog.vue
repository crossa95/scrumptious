<template>
  <div class="backlog">
    <main class="flexbox">
    <b-button size="sm" variant="primary" class="float-right" @click="newCard()">
            Create Card
          </b-button>
      <Board id = "backlogBoard">
        <h1 style="color: white; font-size:30px; text-align: center">Backlog</h1>

        <Card v-for="i in cards" :key="i.title" :id="i.title" :draggable="true" >
            {{i.content}}
        </Card>
        
      </Board>
    </main>
  </div>
</template>

<script>
import Board from '@/components/Board';
import Card from '@/components/Card';
export default {
  name: 'BackLog',
  props: {
    
  },
  components:{
    Board
    ,Card
  },
  data () {
    return {
      cards:[],
      cardsCounter:0
    }
  },
  methods: {
    newCard(){
      var cardText = prompt("What should the card say?");
      var newCard = {title:"card" + this.cardsCounter, content: cardText};
      this.cardsCounter++;
      this.cards.push(newCard);
      
    } 
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