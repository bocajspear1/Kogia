<template>
    <div class="box">
      <h1 class="title">Submission: {{ submission.name }}</h1>
      <h4 class="subtitle is-4">{{ submission.uuid }}</h4>
      
      <div class="level">
        <div class="level-item has-text-centered">
          <div>
            <p class="heading">Submit Date</p>
            <p class="title">{{ submission.submit_time }}</p>
          </div>
        </div>
        <div class="level-item has-text-centered">
          <div>
            <p class="heading">File Count</p>
            <p class="title">{{ fileCount() }}</p>
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
