<template>
    <div
        :id = "id"
        class = "card"
        :draggable = "draggable"
        @dragstart = "dragStart"
        @dragover.stop
    >
        <slot />
    </div>
</template>

<script>
/* eslint-disable */
export default {
    props: ['id', 'draggable'],
    methods: {
        dragStart: e => {
            const target = e.target;
            e.dataTransfer.setData('card_id', target.id);
            setTimeout(() => {
                target.style.display = "none";

            }, 0);
        }
    }
}
</script>
