<script setup>
import SubmissionBlock from '@/components/submission/SubmissionBlock.vue'
import FileList from '../components/file/FileList.vue';
import JobList from '../components/job/JobList.vue';
import MenuButton from '@/components/menu/MenuButton.vue';
import MenuBar from '@/components/menu/MenuBar.vue';
</script>

<template>
  <div class="container column is-10">
    <SubmissionBlock v-if="submission != null" :submission="submission"></SubmissionBlock>
    <MenuBar>
      <template v-slot:main>
        <MenuButton iconname="refresh" @click="getSubmission" tooltip="Refresh"></MenuButton>
        <MenuButton iconname="cog-refresh" @click="resubmitSubmission" tooltip="Resubmit submission"></MenuButton>
        <MenuButton iconname="folder-zip" @click="zipDownload" tooltip="Zipped download"></MenuButton>
          <MenuButton iconname="folder-key" @click="encryptDownload" tooltip="Encrypted download"></MenuButton>
            
        <MenuButton iconname="laptop-account" tooltip="Start manual analysis"></MenuButton>
        
      </template>
      <template v-slot:right>
        <MenuButton iconname="delete" @click="removeSubmission"></MenuButton>
      </template>
    </MenuBar>
    <h4 class="title is-4 is-spaced">Submission Files</h4>
    <FileList v-if="submission != null" :toggle="false" :files="submission.files" @file_clicked="fileClicked"></FileList>
    <h4 class="title is-4 is-spaced">Submission Jobs</h4>
    <JobList v-if="submission != null" :submission_uuid="submission_uuid"></JobList>
  </div>
    
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
      this.$router.push({ name: 'FileSingle', params: { file_uuid: uuid } });
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
      this.$router.push({ name: 'JobCreate', params: { submission_uuid: this.submission_uuid } });
    },
    removeSubmission() {

    },
    zipDownload() {

    },
    encryptDownload() {

    },
  }
}
</script>