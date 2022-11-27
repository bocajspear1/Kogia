<template>
     <table class="table is-striped is-fullwidth is-hoverable" v-if="submissions != undefined && submissions.length > 0">
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
    <div class="notification is-info m-2" v-else>
        No submissions
    </div>
</template>

<style scoped>

</style>

<script>


export default {
  data() {
    return {
      
    }
  },
  props: ["submissions"],
  mounted() {
    
  },
  methods: {
    submissionCount() {
      return this.submissions.length;
    }
  }
}
</script>
