<script setup>
import Paginator from "../general/Paginator.vue";
</script>

<template>
     <table class="table is-striped is-fullwidth is-hoverable" v-if="submissions != undefined && submissions.length > 0 && done == true">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Submission Time</th>
            </tr>
            <tr>
                <td colspan="3">
                    <Paginator :item_total="submission_count" :page_size="page_size" @new_page="onNewPage" :sync_page="current_page"></Paginator>
                </td>
            </tr>
        </thead>
        <tfoot>
          <tr>
                <td colspan="3">
                    <Paginator :item_total="submission_count" :page_size="page_size" @new_page="onNewPage" :sync_page="current_page"></Paginator>
                </td>
            </tr>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Submission Time</th>
            </tr>
        
        </tfoot>

        <tbody>
            <tr v-for="submission in submissions">
                <td><router-link :to="{ name: 'SubmissionSingle', params: { submission_uuid: submission['uuid'] }}">{{ submission['name'] }}</router-link></td>
                <td>{{ submission['description'] }}</td>
                <td>{{ submission['submit_time'] }}</td>
            </tr>
        </tbody>
    </table>
    <div class="notification is-info m-2" v-else-if="done == true">
        No submissions
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
      done: false,
      current_page: 1,
      page_size: 20,
      submission_count: 0,
      submissions: []
    }
  },
  props: ["file_uuid"],
  mounted() {
    this.getSubmissions();
  },
  methods: {
    getSubmissions: function() {

      var self = this;

      var file_item = "";
      if (self.file_uuid != null) {
        file_item = self.file_uuid;
      }

      api.get_submission_list(file_item,
          function(resp_data){
              for (var i in resp_data['submissions']) {
                  var item = resp_data['submissions'][i];
                  item['submit_time'] = time.seconds_to_string(item['submit_time']);
                  self.submissions.push(item);
              }
              self.done = true;
          },
          function(status, data){
              console.log('FAILURE!!', status, data);
          }
      )
    },
    onNewPage: function(page_num) {
        this.current_page = page_num;
        this.getSubmissions();
    }
  }
}
</script>
