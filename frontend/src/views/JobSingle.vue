<script setup>
import SubmissionBlock from '@/components/SubmissionBlock.vue'
import FileDropdown from '../components/file/FileDropdown.vue';
import FileList from '../components/file/FileList.vue';
import SidebarMenuItem from '../components/SidebarMenuItem.vue';
import MenuBar from '../components/MenuBar.vue';
import SidebarMenu from '../components/SidebarMenu.vue';
</script>

<template>
    <div class="column is-2">
        <SidebarMenu>
            <template v-slot:main>
            <SidebarMenuItem iconname="monitor-dashboard" @click="setPage('overview')">Overview</SidebarMenuItem>
            <SidebarMenuItem iconname="desktop-tower-monitor">Host Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="server-network">Network Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="folder-file" @click="setPage('files')">Files</SidebarMenuItem>
            <SidebarMenuItem iconname="table-multiple" @click="setPage('metadata')">Metadata</SidebarMenuItem>
            <SidebarMenuItem iconname="file-chart">Reports</SidebarMenuItem>
            <SidebarMenuItem iconname="script-text">Logs</SidebarMenuItem>
            </template>
        </SidebarMenu>
    </div>
    <div class="container column is-10 pt-6">
        <template v-if="!done">
            <progress class="progress is-medium is-primary m-5" max="100">50%</progress>
        </template>
        <template v-if="done && page == 'overview'">
            <SubmissionBlock v-if="submission != null" :submission="submission"></SubmissionBlock>
        </template>
        <template v-if="done && page == 'files'">
            <FileList v-if="files != null" :toggle="false" :files="files" @file_clicked="fileClicked"></FileList>
        </template>
        <template v-if="done && page == 'metadata'">
            <FileDropdown :files="files" :selected="selected_file" @file_selected="fileSelected"></FileDropdown>
        </template>
        
        
        
        
    </div>
        
    
    <!-- 
    <MenuBar>
      <template v-slot:main>
        <MenuButton iconname="refresh" @click="getSubmission"></MenuButton>
        <MenuButton iconname="cog-refresh" @click="resubmitSubmission"></MenuButton>
        
      </template>
      <template v-slot:right>
        <MenuButton iconname="delete" @click="removeSubmission"></MenuButton>
      </template>
    </MenuBar>
    
    <JobList v-if="submission != null" :submission_uuid="submission_uuid"></JobList> -->
   
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      job: null,
      submission: null,
      files: [],
      job_uuid: "",
      done: false,
      page: null,
      selected_file: null,
    }
  },
  mounted() {
    var self = this;
    this.getJob();
    this._updatePage();
  },
  watch: {
    '$route' (to, from) {
        this._updatePage();
    }
  },
  methods: {
    _updatePage() {
        if (this.$route.params.page) {
            this.page = this.$route.params.page;
        } else {
            this.page = 'overview';
        }
    },
    setPage(page_name) {
        var self = this;
        self.$router.push({ name: 'JobSingle', params: { job_uuid: self.$route.params.job_uuid, page: page_name } });
        self.page = page_name;
    },  
    fileSelected(file) {
        this.selected_file = file;
    },
    fileClicked(uuid, data) {
      this.$router.push({ name: 'FileSingle', params: { file_uuid: uuid } });
    },
    getSubmission(submission_uuid) {
        var self = this;
        axios.get("/api/v1/submission/" + submission_uuid + "/info").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                self.submission = resp_data['result'];
                var date = new Date(self.submission['start_time']*1000);
                self.submission['start_time'] = date.toLocaleString() 
                self.done = true;
                
                // for (var i in self.submission.files) {
                //     self.files.push(self.submission.files[i]);
                // }
                self.files = self.submission.files;
                console.log(self.files);
            }
            
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    },
    getJob() {
      var self = this;
      this.job_uuid = self.$route.params.job_uuid;
      axios.get("/api/v1/job/" + this.job_uuid + "/info").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                self.job = resp_data['result'];
                var date = new Date(self.job['start_time']*1000);
                self.job['start_time'] = date.toLocaleString() 
                console.log(resp_data);
                self.getSubmission(self.job.submission);
            }
            
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    },
  }
}
</script>