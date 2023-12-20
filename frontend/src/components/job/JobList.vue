<script setup>
import Paginator from "../general/Paginator.vue";
</script>

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
            <tr>
                <td :colspan="!submission_uuid ? '6' : '5'">
                    <Paginator :item_total="job_count" :page_size="page_size" @new_page="onNewPage" :sync_page="current_page"></Paginator>
                </td>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <td :colspan="!submission_uuid ? '6' : '5'">
                    <Paginator :item_total="job_count" :page_size="page_size" @new_page="onNewPage" :sync_page="current_page"></Paginator>
                </td>
            </tr>
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
                <td v-if="job['complete'] == true && job['error'] == ''" title="Job complete" class="has-text-success"><mdicon name="check-bold" :size="25" /></td>
                <td v-if="job['error'] != ''" title="Error occured in job" class="has-text-danger"><mdicon name="alert" :size="25" /></td>
                <td v-if="job['complete'] == false && job['error'] == ''" title="Job in progress" class="has-text-info"><mdicon name="clock" :size="25" /></td>
                <td v-if="job['primary'] != null" ><router-link :to="{ name: 'JobSingle', params: { job_uuid: job['uuid'] }}">{{ job['uuid'] }}</router-link></td>
                <td v-if="job['primary'] == null" class="has-text-grey-light">{{ job['uuid'] }}</td>
                <td><router-link v-if="job['primary'] != null" :to="{ name: 'FileSingle', params: { file_uuid: job['primary'] }}">{{ job['primary_name'] }}</router-link></td>
                <td v-if="!submission_uuid"><router-link :to="{ name: 'SubmissionSingle', params: { submission_uuid: job['submission']['uuid'] }}">{{ job['submission']['name'] }}</router-link></td>
                <td>{{ job['start_time'] }}</td>
                <td>{{ job['complete_time'] }}</td>
            </tr>
        </tbody>
    </table>
    <div class="notification is-info m-2" v-else-if="done == true">
        No jobs
    </div>
    <div class="p-3" v-else>
        <progress class="progress is-small is-primary" max="100">50%</progress>
    </div>
</template>

<style scoped>

</style>

<script>
import time from "@/lib/time";
import api from "@/lib/api";

export default {
  data() {
    return {
        jobs: [],
        done: false,
        current_page: 1,
        page_size: 20,
        job_count: 0
    }
  },
  props: ["submission_uuid"],
  mounted() {
    this.getJobs();
  },
  methods: {
    getJobs() {

        var self = this;

        var skip = (self.current_page-1)*self.page_size;
        api.get_job_list(skip, self.page_size, self.submission_uuid, function(data){
            self.job_count = data['total'];
            for (var i in data['jobs']) {
                var item = data['jobs'][i];

                item['complete_time'] = time.seconds_to_string(item['complete_time']);
                item['start_time'] = time.seconds_to_string(item['start_time']);
            }
            self.jobs = data['jobs'];
            self.done = true;
        }, function(status, data) {

        });
    },
    onNewPage: function(page_num) {
        console.log(page_num)
        this.current_page = page_num;
        this.getJobs();
    }
  }
}
</script>