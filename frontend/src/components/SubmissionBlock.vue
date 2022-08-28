<template>
    <div class="box">
      <h1 class="title is-spaced">Submission: {{ submission.name }}</h1>
      <h5 class="subtitle is-5 is-spaced">{{ submission.description }}</h5>
      
      <div class="level">
        <div class="level-item has-text-centered">
          <div>
            <p class="title is-6 is-spaced">Submit Date</p>
            <p class="subtitle is-6">{{ submission.submit_time }}</p>
          </div>
        </div>
        <div class="level-item has-text-centered">
          <div>
            <p class="title is-6 is-spaced">File Count</p>
            <p class="subtitle is-6">{{ fileCount() }}</p>
          </div>
        </div>
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
      
    }
  },
  props: ["submission"],
  mounted() {
    console.log(this.submission)
  },
  methods: {
    fileCount() {
      return this.submission.files.length;
    }
  }
}
</script>
