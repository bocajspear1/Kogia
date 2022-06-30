<template>
    <div class="box is-vcentered has-text-centered">
        <h1 class="title">Waiting for Job...</h1>
        <progress class="progress is-medium is-primary" max="100">50%</progress>
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
  props: ["job_uuid"],
  emits: ["jobdone", "joberror"],
  mounted() {
    this.startWait();
  },
  methods: {
    startWait() {
        var job_uuid = this.job_uuid;
        const interval = setInterval(function() {
            axios.get("api/v1/job/" + job_uuid + "/info").then(function(resp){
                console.log('SUCCESS!!', resp);
                clearInterval(interval);
            }).catch(function(resp){
                console.log('FAILURE!!', resp);
            });
        }, 3000);
    },
    
  }
}
</script>
