<script setup>
import SubmissionBlock from '@/components/submission/SubmissionBlock.vue'
import JobBlock from '@/components/job/JobBlock.vue'
import MetadataViewer from '@/components/metadata/MetadataViewer.vue';
import FileDropdown from '../components/file/FileDropdown.vue';
import JobFilesPanel from '../components/file/JobFilesPanel.vue';
import SidebarMenuItem from '../components/menu/SidebarMenuItem.vue';
import MenuTag from '../components/menu/MenuTag.vue';
import SidebarMenu from '../components/menu/SidebarMenu.vue';
import JobLogViewer from '@/components/job/JobLogViewer.vue';
import JobExport from '@/components/job/JobExport.vue';
import ReportDisplay from '@/components/report/ReportDisplay.vue';
import SignatureList from '@/components/signature/SignatureList.vue';
import ProcessPanel from '@/components/host/ProcessPanel.vue';
import NetworkPanel from '@/components/host/NetworkPanel.vue';
import JobDetails from '@/components/job/JobDetails.vue';
import ScoreTag from '@/components/job/ScoreTag.vue';
</script>

<template>
    <div class="column is-2">
        <SidebarMenu v-if="job != null">
            <template v-slot:main>
            <SidebarMenuItem iconname="monitor-dashboard" @click="setPage('overview')" :active="page=='overview'">
                Overview&nbsp;
                <ScoreTag v-if="job != null && job.primary != null" :score="job.score"></ScoreTag>
            </SidebarMenuItem>
            <SidebarMenuItem iconname="desktop-tower-monitor" @click="setPage('host')" :active="page=='host'" v-if="job.primary != null">
                Host Activity&nbsp;
                <MenuTag v-if="job != null" :value="job.exec_inst_count"></MenuTag>
            </SidebarMenuItem>
            <SidebarMenuItem iconname="server-network" @click="setPage('network')" :active="page=='network'" v-if="job.primary != null">Network Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="folder-file" @click="setPage('files')" :active="page=='files'">
                Files&nbsp;
                <MenuTag v-if="submission != null" :value="submission.files.length"></MenuTag>
            </SidebarMenuItem>
            <SidebarMenuItem iconname="table-multiple" @click="setPage('metadata')" :active="page=='metadata'" v-if="job.primary != null">Metadata</SidebarMenuItem>
            <SidebarMenuItem iconname="file-chart" @click="setPage('reports')" :active="page=='reports'" v-if="job.primary != null">
                Reports&nbsp;
                <MenuTag v-if="job != null" :value="job.report_count"></MenuTag>
            </SidebarMenuItem>
            <SidebarMenuItem iconname="script-text" @click="setPage('logs')" :active="page=='logs'">Logs</SidebarMenuItem>
            <SidebarMenuItem iconname="information" @click="setPage('details')" :active="page=='details'">Details</SidebarMenuItem>
            <SidebarMenuItem iconname="database-export" @click="setPage('export')" :active="page=='export'" v-if="job.primary != null">Export</SidebarMenuItem>
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
                    <div v-if="job.error.length > 0" class="notification  is-warning">
                        <h1 class="is-size-4">Errors</h1>
                        <p v-for="error in job.error">
                            {{  error }}
                        </p>
                    </div>
                    <h1 class="is-size-3">Signatures</h1><br>
                    <SignatureList :signature_matches="all_signatures"></SignatureList>
                </div>
                <!-- <div class="column is-one-third">
                    <ScoreTag :score="job.score"></ScoreTag>
                </div> -->
            </div>
            
        </template>
        <template v-if="done && page == 'host'">
            <ProcessPanel :job_uuid="job_uuid" :selected_instance="selected_instance" @instance_selected="instanceSelected"></ProcessPanel>
        </template>
        <template v-if="done && page == 'network'">
            <NetworkPanel :job_uuid="job_uuid" :selected_instance="selected_instance" @instance_selected="instanceSelected"></NetworkPanel>
        </template>
        <template v-if="done && page == 'files'">
            <JobFilesPanel :files="files"></JobFilesPanel>
        </template>
        <template v-if="done && page == 'metadata'">
            <MetadataViewer :job="job" :selected_file="selected_file" :selected_instance="selected_instance"></MetadataViewer>
        </template>
        <template v-if="done && page == 'reports'">
            <FileDropdown :files="files" :selected="selected_file" @file_selected="fileSelected"></FileDropdown>
            <ReportDisplay :file_uuid="getFileUUID()" :job_uuid="job_uuid"></ReportDisplay>
        </template>
        <template v-if="done && page == 'logs'">
            <JobLogViewer :job_uuid="job_uuid"></JobLogViewer>
        </template>
        <template v-if="done && page == 'details'">
            <JobDetails :job="job"></JobDetails>
        </template>
        <template v-if="done && page == 'export'">
            <JobExport :job="job" :files="files"></JobExport>
        </template>
        
        
        
        
    </div>
   
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
      selected_instance: null,
      selected_process: null,
      logs: [],
      all_signatures: [],
      metadata_selected: 'files'
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
            
            api.get_job_signatures(self.job_uuid, "", 
                function(data) {
                    self.all_signatures = [];
                    for (var i = 0; i < data.length; i++) {
                        self.all_signatures.push(data[i]);
                    }
                },
                function(status, data) {

                }
            )
        } else if (self.page == "logs") {
            
        }
    },
    getFileUUID() {
        if (this.selected_file == null) {
            return null;
        } else {
            return this.selected_file['uuid'];
        }
    },  
    getInstanceUUID() {
        console.log(this.selected_instance)
        if (this.selected_instance == null) {
            return null;
        } else {
            return this.selected_instance['uuid'];
        }
    },  
    getProcessUUID() {
        console.log(this.selected_process)
        if (this.selected_process == null) {
            return null;
        } else {
            return this.selected_process['uuid'];
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
    instanceSelected(instance) {
        var self = this;
        api.get_instance_data(instance.uuid,
            function(data) {
                data = time.add_pretty_times(data, ['start_time', 'end_time'], [['start_time', 'end_time', 'duration']]);
                self.selected_instance = data;
                self.selected_process = null;
            },
            function(status, data) {

            }
        )
    },
    processSelected(process) {
        this.selected_process = process;
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