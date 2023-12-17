<template>
    <div class="box">
      <h4 class="title is-spaced is-4">Submission: {{ submission.name }}</h4>
      <h6 class="subtitle is-6 is-spaced">{{ submission.description }}</h6>
      
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
        <div class="level-item has-text-centered">
          <div>
            <p class="title is-6 is-spaced">Submitter</p>
            <p class="subtitle is-6">{{ submission.owner }}</p>
          </div>
        </div>
      </div>
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
  props: ["submission"],
  mounted() {
    
  },
  methods: {
    fileCount() {
      return this.submission.files.length;
    }
  }
}
</script>
