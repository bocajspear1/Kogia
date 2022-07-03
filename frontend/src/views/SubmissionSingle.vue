<script setup>
import SubmissionBlock from '@/components/SubmissionBlock.vue'
import FileList from '../components/FileList.vue';
</script>

<template>
    <SubmissionBlock v-if="submission != null" :submission="submission"></SubmissionBlock>
    <FileList v-if="submission != null" :files="submission.files"></FileList>
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      submission: null
    }
  },
  mounted() {
    this.getSubmission();
  },
  methods: {
    getSubmission() {
      var self = this;
      var submission_uuid = self.$route.params.submission_uuid;
      axios.get("/api/v1/submission/" + submission_uuid + "/info").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                self.submission = resp_data['result'];
                var date = new Date(self.submission['submit_time']*1000);
                self.submission['submit_time'] = date.toLocaleString() 
                self.done = true;
            }
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>