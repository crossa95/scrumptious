<template>
  <div class="backlog">
    <main class="flexbox">
      <Board id = "board-1">
        <h1 style="color: white; font-size:30px; text-align: center">Backlog</h1>
        <Card v-for="(todo) in todos" v-bind:key="todo.card_id"  v-bind:draggable="true">
          <p class="text-left">{{todo.card_description}}</p>
        </Card>
      </Board>
    </main>
  </div>
</template>

<script>
/* eslint-disable */
import axios from 'axios'
import Board from '@/components/Board';
import Card from '@/components/Card';
export default {
  name: 'BackLog',
  props: {

  },
  components:{
    Board,
    Card
  },
  data () {
    return {
      todos: [],
      card_id: '',
      taskname: '',
      isEdit: false
    }
  },
  mounted () {
    this.getTasks()
  },
  methods: {
    getTasks () {
      axios({ method: 'GET', url: '/api/cards' }).then(
        result => {
          console.log(result.data)
          this.todos = result.data

        },
        error => {
          console.error(error)
        }
      )
    },
    addNewTask () {
      axios.post('/api/card',
        { card_description: this.taskname })
        .then((res) => {
          this.taskname = ''
          this.getTasks()
          console.log(res)
        })
        .catch(err => {
          console.log(err)
        })
    },
    editTask (card_description, card_id) {
      this.card_id = card_id
      this.taskname = card_description
      this.isEdit = true
    },
    updateTask () {
      axios.put(`/api/card/${this.card_id}`,
        { card_description: this.taskname })
        .then(res => {
          this.taskname = ''
          this.isEdit = false
          this.getTasks()
          console.log(res)
        })
        .catch(err => {
          console.log(err)
        })
    },
    deleteTask (card_id) {
      axios.delete(`/api/card/${card_id}`)
        .then(res => {
          this.taskname = ''
          this.getTasks()
          console.log(res)
        })
        .catch(err => {
          console.log(err)
        })
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
