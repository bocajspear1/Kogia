<script setup>
import FileList from '@/components/file/FileList.vue';
import PluginCard from '@/components/plugin/PluginCard.vue';
import Notifications from '@/components/general/Notifications.vue';
</script>


<template>
<div class="container column is-10">
  <Notifications ref="notifications"></Notifications>
  <div class="box" v-if="submission != null">
      <h1 class="title is-spaced">Submission: {{ submission.name }}</h1>
      <h5 class="subtitle is-5 is-spaced">{{ submission.description }}</h5>
      <div class="buttons">
        <button class="button is-success" ref="createButton" disabled @click="createJob">Create Job</button>
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
      <h5 class="title is-5" title="Dynamically executes the submission to get syscalls and other info">Syscall</h5>
      <div v-for="plugin in plugins">
        <PluginCard v-if="plugin.type == 'syscall'" :plugin="plugin"></PluginCard>
      </div>
    </div>
    <div class="column">
      <h5 class="title is-5" title="Extracts metadata from the submission">Metadata</h5>
      <div v-for="plugin in plugins">
        <PluginCard v-if="plugin.type == 'metadata'" :plugin="plugin"></PluginCard>
      </div>
    </div>
    <div class="column">
      <h5 class="title is-5" title="Runs scanning tools and runs analysis against extracted data">Signature</h5>
      <div v-for="plugin in plugins">
        <PluginCard v-if="plugin.type == 'signature'" :plugin="plugin"></PluginCard>
      </div>
    </div>
  </div>
</div>
  
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";

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
    createJob() {
      
      console.log(this.primary_file);
      console.log(this.plugins);
      var plugin_list = [];
      for (var i in this.plugins) {
        if (this.plugins[i].enabled == true) {
          var plugin_data = {
            "name": this.plugins[i].name,
            "options": {}
          };

          for (var o in this.plugins[i].options) {
            var option = this.plugins[i].options[o];
            plugin_data['options'][option['name']] = option['value']
          }
          plugin_list.push(plugin_data);
        }
      }
      
      var self = this;

      api.do_create_analysis(this.submission_uuid, this.primary_file, plugin_list,
      function(result) {

      },
      function(status, error){
        console.log(resp)
        self.$refs.notifications.addNotification("error", "Analysis Create Error: " + error);
      });
    },
    getSubmission() {
      var self = this;
      this.submission_uuid = self.$route.params.submission_uuid;
      api.get_submission_info(this.submission_uuid, function(result) {
        self.submission = result;
        var date = new Date(self.submission['submit_time']*1000);
        self.submission['submit_time'] = date.toLocaleString() 
        self.done = true;
      }, function(status, error) {
        self.$refs.notifications.addNotification("error", "Error getting submission: " + error);
      })
    },
    getPlugins() {
      var self = this;
      api.get_plugin_list(function(result) {
        const shown_plugin_types = ['syscall', 'metadata', 'signature'];
        var new_list = [];
        
        for (var i in result) {
          var item = result[i];
          if (shown_plugin_types.includes(item['type'])) {
            item['enabled'] = true;
            new_list.push(item);
          }
        }

        self.plugins = new_list;

      }, function(status, error){
        self.$refs.notifications.addNotification("error", "Error getting plugin kist: " + error);
      })
      
    }
  }
}
</script>
