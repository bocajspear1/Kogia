<script setup>
import SubmissionBlock from '@/components/SubmissionBlock.vue'
import FileList from '../components/FileList.vue';
import JobList from '../components/JobList.vue';
import SidebarMenuItem from '../components/SidebarMenuItem.vue';
import MenuBar from '../components/MenuBar.vue';
import SidebarMenu from '../components/SidebarMenu.vue';
</script>

<template>
    <div class="column is-2">
        <SidebarMenu>
            <template v-slot:main>
            <SidebarMenuItem iconname="monitor-dashboard">Overview</SidebarMenuItem>
            <SidebarMenuItem iconname="desktop-tower-monitor">Host Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="server-network">Network Activity</SidebarMenuItem>
            <SidebarMenuItem iconname="folder-file">Files</SidebarMenuItem>
            <SidebarMenuItem iconname="table-multiple">Metadata</SidebarMenuItem>
            <SidebarMenuItem iconname="file-chart">Reports</SidebarMenuItem>
            </template>
        </SidebarMenu>
    </div>
    <div class="container column is-10">
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
        <div>aaa</div>
    </div>
        <div>aaa</div>
    
    <!-- <SubmissionBlock v-if="submission != null" :submission="submission"></SubmissionBlock>
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
    <JobList v-if="submission != null" :submission_uuid="submission_uuid"></JobList> -->
   
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      submission: null,
      job_uuid: ""
    }
  },
  mounted() {
    this.getJob();
  },
  methods: {
    fileClicked(uuid, data) {
      this.$router.push({ name: 'FileSingle', params: { file_uuid: uuid } });
    },
    getJob() {
      var self = this;
      this.job_uuid = self.$route.params.job_uuid;
      axios.get("/api/v1/job/" + this.job_uuid + "/info").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                self.submission = resp_data['result'];
                var date = new Date(self.submission['start_time']*1000);
                self.submission['start_time'] = date.toLocaleString() 
                self.done = true;
                console.log(resp_data)
            }
            
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    },
  }
}
</script>