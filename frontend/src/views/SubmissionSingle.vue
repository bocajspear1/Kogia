<script setup>
import SubmissionBlock from '@/components/SubmissionBlock.vue'
import FileList from '../components/FileList.vue';
import MenuButton from '../components/MenuButton.vue';
import MenuBar from '../components/MenuBar.vue';
</script>

<template>
    <SubmissionBlock v-if="submission != null" :submission="submission"></SubmissionBlock>
    <MenuBar>
      <template v-slot:main>
        <MenuButton iconname="refresh" @click="getSubmission"></MenuButton>
        <MenuButton iconname="cog-refresh" @click="resubmitSubmission"></MenuButton>
        
      </template>
      <template v-slot:right>
        <MenuButton iconname="delete" @click="removeSubmission"></MenuButton>
      </template>
    </MenuBar>
    <FileList v-if="submission != null" :toggle="false" :files="submission.files" @file_clicked="fileClicked"></FileList>
    
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      submission: null,
      submission_uuid: ""
    }
  },
  mounted() {
    this.getSubmission();
  },
  methods: {
    fileClicked(uuid, data) {
      console.log(uuid, data);
      this.$router.push({ name: 'FileSingle', params: { file_uuid: uuid } })
    },
    getSubmission() {
      var self = this;
      this.submission_uuid = self.$route.params.submission_uuid;
      axios.get("/api/v1/submission/" + this.submission_uuid + "/info").then(function(resp){
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
    },
    resubmitSubmission() {
      this.$router.push({ name: 'JobCreate', params: { submission_uuid: this.submission_uuid } })
    },
    removeSubmission() {

    }
  }
}
</script>