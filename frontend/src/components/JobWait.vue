<template>
    <div class="box is-vcentered has-text-centered">
        <h1 class="title">Waiting for Job...</h1>
        <progress class="progress is-medium is-primary" max="100">50%</progress>
    </div> 
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";

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
        var self = this;
        var job_uuid = this.job_uuid;
        const interval = setInterval(function() {
          api.get_job_info(job_uuid, function(result) {
            var is_complete = result['complete'];
            if (is_complete) {
                self.$emit('jobdone', result);
                clearInterval(interval);
            }
          }, function(status, error) {
            console.log('FAILURE!!', status, error);
          });
        }, 3000);
    },
    
  }
}
</script>
