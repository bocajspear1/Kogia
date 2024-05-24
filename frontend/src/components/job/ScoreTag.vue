<script setup>

</script>

<template>
    <span class="tag is-info" v-if="score < 10">{{ score_rounded }} / 100</span>
    <span class="tag is-warning" v-else-if="score < 50 && score >= 10">{{ score_rounded }} / 100</span>
    <span class="tag is-danger" v-else-if="score >= 50">{{ score_rounded }} / 100</span>
    <span class="tag is-light" v-else>??? / 100</span>
</template>

<style scoped>

</style>

<script>
export default {
    data() {
        return {
            
        }
    },
    props: ["score"],
    mounted() {
        
    },
    computed: {
        score_rounded() {
            return (Math.round(this.score * 100) / 100)
        }
    },
    methods: {
    
    }
}
</script>