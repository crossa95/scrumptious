<template>
      <div>
        {{ message.content }}
      </div>
</template>

<script>
/* eslint-disable */
export default {
  name: 'ChatMessage',
  props:{
      message: {
        channel: Number,
        content: String
      }
  }
}
</script>

