<script setup>

</script>

<template>
<div class="container column is-10">
    <div class="content">
        <img class="logo-img" :src="getHomeImage()"/>
    </div>
    <div class="level">
    <div class="level-item has-text-centered">
        <div>
            <p class="heading">Version</p>
            <p class="title">{{ version }}</p>
        </div>
    </div>
    <div class="level-item has-text-centered">
        <div>
            <p class="heading">Submission Count</p>
            <p class="title">{{ submission_count }}</p>
        </div>
    </div>
    <div class="level-item has-text-centered">
        <div>
            <p class="heading">File Count</p>
            <p class="title">{{ file_count }}</p>
        </div>
    </div>
    <div class="level-item has-text-centered">
        <div>
            <p class="heading">Job Count</p>
            <p class="title">{{ job_count }}</p>
        </div>
    </div>
  </div>

</div>
  
</template>

<style scoped>
    .logo-img {
        width: 35%;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
</style>


<script>
import time from "@/lib/time";
import api from '@/lib/api';

export default {
  data() {
    return {
        version: "?",
        submission_count: 0,
        file_count: 0,
        job_count: 0,
    }
  },
  mounted() {
    this.updateStats();
  },   
  methods: {
    updateStats() {
        var self = this;
        api.get_system_stats(function(data) {
            self.version = data['version'];
            self.submission_count = data['submission_count'];
            self.file_count = data['file_count'];
            self.job_count = data['job_count'];
        },
        function(status, data) {
            self.done = true;
            console.log('FAILURE!!', status, data);
        })
    },
    
    getHomeImage() {
        return "/images/" + import.meta.env.VITE_IMAGE_PREFIX + ".png"
    },
  }
}
</script>