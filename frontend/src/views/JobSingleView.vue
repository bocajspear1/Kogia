<script setup>
import SubmissionBlock from '@/components/submission/SubmissionBlock.vue'
import JobBlock from '@/components/job/JobBlock.vue'
import MetadataTable from '@/components/metadata/MetadataTable.vue';
import FileDropdown from '../components/file/FileDropdown.vue';
import FileList from '../components/file/FileList.vue';
import SidebarMenuItem from '../components/menu/SidebarMenuItem.vue';
import MenuBar from '../components/menu/MenuBar.vue';
import SidebarMenu from '../components/menu/SidebarMenu.vue';
import DynamicFilterTable from '@/components/dynamic/DynamicFilterTable.vue';
import ReportDisplay from '@/components/report/ReportDisplay.vue';
import SignatureList from '@/components/signature/SignatureList.vue';
import ProcessPanel from '@/components/host/ProcessPanel.vue';
</script>

<template>
    <div class="column is-2">
        <SidebarMenu>
            <template v-slot:main>
            <SidebarMenuItem iconname="monitor-dashboard" @click="setPage('overview')" :active="page=='overview'">Overview</SidebarMenuItem>
            <SidebarMenuItem iconname="desktop-tower-monitor" @click="setPage('host')" :active="page=='host'">Host Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="server-network">Network Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="folder-file" @click="setPage('files')" :active="page=='files'">Files</SidebarMenuItem>
            <SidebarMenuItem iconname="table-multiple" @click="setPage('metadata')" :active="page=='metadata'">Metadata</SidebarMenuItem>
            <SidebarMenuItem iconname="file-chart" @click="setPage('reports')" :active="page=='reports'">Reports</SidebarMenuItem>
            <SidebarMenuItem iconname="script-text" @click="setPage('logs')" :active="page=='logs'">Logs</SidebarMenuItem>
            <SidebarMenuItem iconname="information" @click="setPage('details')" :active="page=='details'">Details</SidebarMenuItem>
            <SidebarMenuItem iconname="database-export" @click="setPage('export')" :active="page=='export'">Export</SidebarMenuItem>
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
            
            <div class="columns">
                <div class="column">
                    <h1 class="is-size-3">Signatures</h1>
                    <SignatureList :signatures="all_signatures"></SignatureList>
                </div>
                <div class="column">
                    Second column
                </div>
            </div>
            
        </template>
        <template v-if="done && page == 'host'">
            <ProcessPanel :job_uuid="job_uuid"></ProcessPanel>
        </template>
        <template v-if="done && page == 'files'">
            <FileList v-if="files != null" :toggle="false" :files="files" @file_clicked="fileClicked"></FileList>
        </template>
        <template v-if="done && page == 'metadata'">
            <FileDropdown :files="files" :selected="selected_file" @file_selected="fileSelected"></FileDropdown>
            <MetadataTable :file_uuid="getFileUUID()"></MetadataTable>
        </template>
        <template v-if="done && page == 'reports'">
            <FileDropdown :files="files" :selected="selected_file" @file_selected="fileSelected"></FileDropdown>
            <ReportDisplay :file_uuid="getFileUUID()" :job_uuid="job_uuid"></ReportDisplay>
        </template>
        <template v-if="done && page == 'logs'">
            <DynamicFilterTable :columns="['Severity', 'Name', 'Message']" 
                                :data="logs" 
                                :noFilter="['Message']"
                                :limitFilter="{'Severity':['error', 'warning', 'debug', 'info']}"
                                @onFilter="onLogFilter"></DynamicFilterTable>
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
      logs: [],
      all_signatures: []
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
        var self = this;

        if (self.page == 'overview' || self.page == '') {
            self.all_signatures = [];
            api.get_job_signatures(self.job_uuid, "", 
                function(data) {
                    for (var i = 0; i < data.length; i++) {
                        self.all_signatures.push(data[i]);
                    }
                },
                function(status, data) {

                }
            )
        } else if (self.page == "logs") {
            self.logs = [];
            api.get_job_logs(self.job_uuid, "", 
                function(data) {
                    for (var i = 0; i < data.length; i++) {
                        var message = data[i]['message']
                        self.logs.push([data[i]['severity'], data[i]['log_name'], message]);
                    }
                },
                function(status, data) {

                }
            )
        }
    },
    getFileUUID() {
        if (this.selected_file == null) {
            return null;
        } else {
            return this.selected_file['uuid'];
        }
    },  
    setPage(page_name) {
        var self = this;
        self.$router.push({ name: 'JobSingle', params: { job_uuid: self.$route.params.job_uuid, page: page_name } });
        self.page = page_name;
    },  
    onLogFilter(column, new_filter) {
        console.log(column, new_filter);
    },
    fileSelected(file) {
        this.selected_file = file;
    },
    fileClicked(uuid, data) {
      this.$router.push({ name: 'FileSingle', params: { file_uuid: uuid } });
    },
    getSubmission(submission_uuid) {
        var self = this;
        
        api.get_submission_info(submission_uuid, function(result) {
            self.submission = result;
            self.submission['submit_time'] = time.seconds_to_string(self.submission['submit_time']);
            self.done = true;
            self.files = self.submission.files;
        }, function(status, error){
            console.log('FAILURE!!', status, error);
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