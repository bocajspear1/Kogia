<template>
    <div class="box">
      <h4 class="title is-spaced is-4">Job {{ job.uuid }}</h4>

      <h5 class="title is-spaced is-5">Runner: {{ job.runner }}</h5>
      
      <table class="table is-striped is-fullwidth">
        <thead>
            <tr>
                <th>Plugin</th>
                <th>Arguments</th>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <th>Plugin</th>
                <th>Arguments</th>
            </tr>    
        </tfoot>

        <tbody>
            <tr v-for="plugin in job.plugins">
                <td>{{ plugin }}</td>
                <td>{{ job.plugin_args[plugin] }}</td>
            </tr>
        </tbody>
    </table>
      
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
    
  },
  methods: {
    
  }
}
</script>
