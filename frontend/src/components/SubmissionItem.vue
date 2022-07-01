<template>
    <div class="box is-vcentered has-text-centered">
        <h1 class="title">{{ submission.name }}</h1>
        <h3 class="subtitle is-3">{{ submission.uuid }}</h3>
    </div> 
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      
    }
  },
  props: ["submission"],
  mounted() {
    
  },
  methods: {
    
  }
}
</script>
