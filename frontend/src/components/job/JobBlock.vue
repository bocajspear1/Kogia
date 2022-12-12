<template>
    <div class="box">
      <h4 class="title is-spaced is-4">Job {{ job.uuid }}</h4>
      
      
      <div class="level">
        <div class="level-item has-text-centered">
            <div>
                <p class="title is-6 is-spaced">Started</p>
                <p class="subtitle is-6">{{ job.start_time_string }}</p>
            </div>
        </div>
        <div class="level-item has-text-centered">
            <div>
                <p class="title is-6 is-spaced">Completed</p>
                <p class="subtitle is-6">{{ job.complete_time_string }}</p>
            </div>
        </div>
        <div class="level-item has-text-centered">
            <div>
                <p class="title is-6 is-spaced">Duration</p>
                <p class="subtitle is-6">{{ job.duration }}</p>
            </div>
        </div>
      </div>
    </div> 
</template>

<style scoped>

</style>

<script>
import time from "@/lib/time";

export default {
  data() {
    return {
      
    }
  },
  props: ["job"],
  mounted() {
    var self = this;
    var start_seconds = self.job['start_time'];
    self.job['start_time_string'] = time.seconds_to_string(start_seconds);
    if (self.job['complete_time']) {
        var complete_seconds = self.job['complete_time'];
        self.job['complete_time_string'] = time.seconds_to_string(complete_seconds);
        self.job['duration'] = time.seconds_duration(start_seconds, complete_seconds);
    } else {
        self.job['complete_time_string'] = "Running"
        self.job['duration'] = ""
    }
  },
  methods: {
    
  }
}
</script>
