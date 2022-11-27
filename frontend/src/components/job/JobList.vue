<template>
    <table class="table is-striped is-fullwidth is-hoverable" v-if="jobs.length > 0 && done == true">
        <thead>
            <tr>
                <th>Status</th>
                <th>UUID</th>
                <th>Primary</th>
                <th v-if="!submission_uuid">Submission</th>
                <th>Start Time</th>
                <th>End Time</th>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <th>Status</th>
                <th>UUID</th>
                <th>Primary</th>
                <th v-if="!submission_uuid">Submission</th>
                <th>Start Time</th>
                <th>End Time</th>
            </tr>
        
        </tfoot>

        <tbody>
            <tr v-for="job in jobs">
                <td v-if="job['complete'] == true && job['error'] == ''" title="Job complete"><mdicon name="check-bold" :size="25" /></td>
                <td v-if="job['error'] != ''" title="Error occured in job"><mdicon name="alert" :size="25" /></td>
                <td v-if="job['complete'] == false && job['error'] == ''" title="Job in progress"><mdicon name="clock" :size="25" /></td>
                <td v-if="job['primary'] != null" ><router-link :to="{ name: 'JobSingle', params: { job_uuid: job['uuid'] }}">{{ job['uuid'] }}</router-link></td>
                <td v-if="job['primary'] == null" >{{ job['uuid'] }}</td>
                <td><router-link v-if="job['primary'] != null" :to="{ name: 'FileSingle', params: { file_uuid: job['primary'] }}">{{ job['primary_name'] }}</router-link></td>
                <td v-if="!submission_uuid"><router-link :to="{ name: 'SubmissionSingle', params: { submission_uuid: job['submission']['uuid'] }}">{{ job['submission']['name'] }}</router-link></td>
                <td>{{ job['start_time'] }}</td>
                <td>{{ job['complete_time'] }}</td>
            </tr>
        </tbody>
    </table>
    <div class="notification is-info" v-else-if="done == true">
        No jobs
    </div>
    <div class="p-3" v-else>
        <progress class="progress is-small is-primary" max="100">50%</progress>
    </div>
</template>

<style scoped>

</style>

<script>
import axios from 'axios';
import time from "@/lib/time";

export default {
  data() {
    return {
        jobs: [],
        done: false
    }
  },
  props: ["submission_uuid"],
  mounted() {
    this.getJobs();
  },
  methods: {
    getJobs() {

        var self = this;
        var url = "/api/v1/job/list";

        if (self.submission_uuid != null) {
            url += "?submission=" + self.submission_uuid;
        }

        axios.get(url).then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                for (var i in resp_data['result']) {
                    var item = resp_data['result'][i];

                    item['complete_time'] = time.seconds_to_string(item['complete_time']);
                    item['start_time'] = time.seconds_to_string(item['start_time']);
                }
                self.jobs = resp_data['result'];
                self.done = true;
            }
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>