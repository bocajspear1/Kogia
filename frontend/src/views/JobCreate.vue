<script setup>
import FileList from '../components/FileList.vue';
import PluginCard from '../components/PluginCard.vue';
</script>


<template>
  <div class="box" v-if="submission != null">
      <h1 class="title is-spaced">Submission: {{ submission.name }}</h1>
      <h5 class="subtitle is-5 is-spaced">{{ submission.description }}</h5>
      <div class="buttons">
        <button class="button is-success" ref="createButton" disabled>Create Job</button>
      </div>
  </div>
  <h3 class="subtitle is-spaced is-3">Select primary file:</h3>
  <p>
    Primary file is the file executed during dynamic analysis.
  </p>
  <FileList v-if="submission != null" :toggle="true" :files="submission.files" @file_clicked="fileClicked"></FileList>
  <h3 class="subtitle is-spaced is-3">Select plugins:</h3>
  <div class="columns">
    <div class="column">
      <h5 class="title is-5">Metadata</h5>
      <div v-for="plugin in plugins">
        <PluginCard v-if="plugin.type == 'metadata'" :plugin="plugin"></PluginCard>
      </div>
    </div>
    <div class="column">
      <h5 class="title is-5">Syscall</h5>
      <div v-for="plugin in plugins">
        <PluginCard v-if="plugin.type == 'syscall'" :plugin="plugin"></PluginCard>
      </div>
    </div>
    <div class="column">
      <h5 class="title is-5">Signature</h5>
      <div v-for="plugin in plugins">
        <PluginCard v-if="plugin.type == 'signature'" :plugin="plugin"></PluginCard>
      </div>
    </div>
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
      submission_uuid: "",
      plugins: [],
      primary_file: null
    }
  },
  props: [],
  mounted() {
    var self = this;
      this.submission_uuid = self.$route.params.submission_uuid;
      this.getSubmission();
      this.getPlugins();
      
  },
  methods: {
    fileClicked(uuid, file_data, toggled) {
      console.log(uuid, file_data)
      
      if (toggled) {
        this.primary_file = uuid;
        this.$refs.createButton.removeAttribute('disabled');
      } else {
        this.primary_file = null;
        this.$refs.createButton.setAttribute('disabled', '');
      }
      
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
    getPlugins() {
      var self = this;
      axios.get("/api/v1/plugin/list").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
              
              
              for (var i in resp_data['result']) {
                resp_data['result'][i]['enabled'] = true;
              }
              self.plugins = resp_data['result'];
            }
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>
