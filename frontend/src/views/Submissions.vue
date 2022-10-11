<template>
<div class="container column is-10">
    <table class="table is-striped is-fullwidth is-hoverable" v-if="submissions.length > 0 && done == true">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Submission Time</th>
            </tr>
        </thead>
        <tfoot>
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
    <div class="notification is-info" v-else-if="done == true">
        Add file above, or drag a file onto the bar
    </div>
    <div class="p-3" v-else>
        <progress class="progress is-small is-primary" max="100">50%</progress>
    </div>
</div>
    
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
        submissions: [],
        done: false
    }
  },
  mounted() {
    this.getSubmissions();
  },
  methods: {
    getSubmissions() {

        var self = this;

        axios.get("/api/v1/submission/list").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                for (var i in resp_data['result']) {
                    var item = resp_data['result'][i];
                    var date = new Date(item['submit_time']*1000 );
                    // item['submit_time'] = date.getFullYear() + "/" + date.getDate() + "/" + (date.getMonth()+1) + 
                    //     " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
                    item['submit_time'] = date.toLocaleString() 
                }
                self.submissions = resp_data['result'];
                self.done = true;
            }
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>