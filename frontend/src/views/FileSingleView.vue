<script setup>
import FileInfoBlock from '@/components/file/FileInfoBlock.vue';
import Progress from '@/components/general/Progress.vue';
import MenuButton from '@/components/menu/MenuButton.vue';
import MenuBar from '@/components/menu/MenuBar.vue';
import SubmissionList from '@/components/submission/SubmissionList.vue';
import MetadataTable from '@/components/metadata/MetadataTable.vue';
</script>

<template>

<div class="container column is-10">
    <template  v-if="file != null && done == true">
         <FileInfoBlock :file="file"></FileInfoBlock>
         <MenuBar>
          <template v-slot:main>
            <MenuButton iconname="download" @click="download" tooltip="Raw download"></MenuButton>
            <MenuButton iconname="folder-zip" @click="zip_download" tooltip="Zipped download"></MenuButton>
            <MenuButton iconname="folder-key" @click="encrypt_download" tooltip="Encrypted download"></MenuButton>
            
            
          </template>
          <template v-slot:right>
            
          </template>
        </MenuBar>
        <div class="tabs">
            <ul>
                <li :class="tab == 'submissions' ? 'is-active' : ''"><a @click="setTab('submissions')">Submissions</a></li>
                <li :class="tab == 'metadata' ? 'is-active' : ''"><a @click="setTab('metadata')">Metadata</a></li>
            </ul>
        </div>
    </template>

   
    <Progress v-if="file != null && done != true"></Progress>
    <div v-if="file == null && done == true" class="notification is-warning">
        File not found
    </div>
    <template v-if="data_done && (tab == 'submissions')">
      <SubmissionList :submissions="submissions"></SubmissionList>
    </template>
    <template v-if="data_done && (tab == 'metadata')">
      <MetadataTable :file_uuid="getFileUUID()"></MetadataTable>
    </template>
</div>
    
</template>

<style scoped>

</style>

<script>
import time from "@/lib/time";
import api from '@/lib/api';

export default {
  data() {
    return {
      file: null,
      done: false,
      data_done: false,
      tab: "",
      submissions: []
    }
  },
  mounted() {
    this.getFile();
    this.setTab("submissions");
  },
  methods: {
    fileClicked(uuid, data) {
      console.log(uuid, data);
    },
    getFileUUID() {
        if (this.file == null) {
            return null;
        } else {
            return this.file['uuid'];
        }
    },  
    getFile() {
        var self = this;
        var file_uuid = self.$route.params.file_uuid;
        api.get_file_info(file_uuid,
            function(data) {
                self.file = data;
                self.done = true;
            },
            function(status, data) {
                self.done = true;
                console.log('FAILURE!!', status, data);
            }
        );
    },
    download() {

    },
    zip_download() {

    },
    encrypt_download() {

    },
    setTab(new_tab) {
      var self = this;
      self.tab = new_tab;
      if (new_tab == 'submissions') {
        console.log("hi")
        self.submissions = [];
        var file_uuid = self.$route.params.file_uuid;
        self.data_done = false;
        api.get_submission_list(file_uuid,
            function(resp_data){
                for (var i in resp_data) {
                    var item = resp_data[i];
                    item['submit_time'] = time.seconds_to_string(item['submit_time']);
                    self.submissions.push(item);
                }
                self.data_done = true;
                console.log(self.submissions)
            },
            function(status, data){
                console.log('FAILURE!!', status, data);
            }
        )
      }
    }
  }
}
</script>