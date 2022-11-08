<script setup>
import SubmissionBlock from '@/components/submission/SubmissionBlock.vue'
import JobBlock from '@/components/job/JobBlock.vue'
import FileDropdown from '../components/file/FileDropdown.vue';
import FileList from '../components/file/FileList.vue';
import SidebarMenuItem from '../components/menu/SidebarMenuItem.vue';
import MenuBar from '../components/menu/MenuBar.vue';
import SidebarMenu from '../components/menu/SidebarMenu.vue';
</script>

<template>
    <div class="column is-2">
        <SidebarMenu>
            <template v-slot:main>
            <SidebarMenuItem iconname="monitor-dashboard" @click="setPage('overview')" :active="page=='overview'">Overview</SidebarMenuItem>
            <SidebarMenuItem iconname="desktop-tower-monitor">Host Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="server-network">Network Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="folder-file" @click="setPage('files')" :active="page=='files'">Files</SidebarMenuItem>
            <SidebarMenuItem iconname="table-multiple" @click="setPage('metadata')" :active="page=='metadata'">Metadata</SidebarMenuItem>
            <SidebarMenuItem iconname="file-chart">Reports</SidebarMenuItem>
            <SidebarMenuItem iconname="script-text" @click="setPage('logs')" :active="page=='logs'">Logs</SidebarMenuItem>
            </template>
        </SidebarMenu>
    </div>
    <div class="container column is-10 pt-6">
        <template v-if="!done">
            <progress class="progress is-medium is-primary m-5" max="100">50%</progress>
        </template>
        <template v-if="done && page == 'overview'">
            <JobBlock v-if="job != null" :job="job"></JobBlock>
            <SubmissionBlock v-if="submission != null" :submission="submission"></SubmissionBlock>
        </template>
        <template v-if="done && page == 'files'">
            <FileList v-if="files != null" :toggle="false" :files="files" @file_clicked="fileClicked"></FileList>
        </template>
        <template v-if="done && page == 'metadata'">
            <FileDropdown :files="files" :selected="selected_file" @file_selected="fileSelected"></FileDropdown>
        </template>
        <template v-if="done && page == 'logs'">
            
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
import api from '@/lib/api';
import time from "@/lib/time";

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
        if (self.page == 'metadata') {
            axios.get("/api/v1/file/" + self.selected_file['uuid'] + "/metadata/list").then(function(resp){
                var resp_data = resp['data'];

                if (resp_data['ok'] == true) {
                    console.log(resp_data['result']);
                }
                
                
            }).catch(function(resp){
                console.log('FAILURE!!', resp);
            });
        }
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
                self.submission['submit_time'] = time.seconds_to_string(self.submission['submit_time']);
                self.done = true;
                self.files = self.submission.files;
            }
            
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    },
    getJob() {
        var self = this;
        this.job_uuid = self.$route.params.job_uuid;
        api.get_job_info(this.job_uuid, 
            function(data) {
                self.job = data;
                
                
                console.log(self.job);
                self.getSubmission(self.job.submission);
            },
            function(status, data){
                console.log('failed', status, data);
            }
        );
    },
  }
}
</script>