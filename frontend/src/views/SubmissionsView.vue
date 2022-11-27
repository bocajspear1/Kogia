<script setup>
import SubmissionList from '@/components/submission/SubmissionList.vue'
</script>
<template>
<div class="container column is-10">
    <SubmissionList v-if="done == true" :submissions="submissions"></SubmissionList>
    <div class="p-3" v-else>
        <progress class="progress is-small is-primary" max="100">50%</progress>
    </div>
</div>
    
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";
import time from "@/lib/time";

export default {
  data() {
    return {
        submissions: [],
        done: false
    }
  },
  mounted() {
    this.getSubmissions();
  },
  methods: {
    getSubmissions() {

        var self = this;

        api.get_submission_list("",
            function(resp_data){
                for (var i in resp_data) {
                    var item = resp_data[i];
                    item['submit_time'] = time.seconds_to_string(item['submit_time']);
                    self.submissions.push(item);
                }
                self.done = true;
            },
            function(status, data){
                console.log('FAILURE!!', status, data);
            }
        )
    }
  }
}
</script>