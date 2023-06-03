<script setup>
var submission_count = "N/A"
var unique_file_count = "N/A"
var total_file_count = "N/A"
</script>

<template>
<div class="container column is-10">
    <div class="content">
        <img class="logo-img" src="/images/kogia.png"/>
    </div>
    <div class="level">
    <div class="level-item has-text-centered">
        <div>
            <p class="heading">Submissions</p>
            <p class="title">{{ submission_count }}</p>
        </div>
    </div>
    <div class="level-item has-text-centered">
        <div>
            <p class="heading">Unique Files</p>
            <p class="title">{{ unique_file_count }}</p>
        </div>
    </div>
    <div class="level-item has-text-centered">
        <div>
            <p class="heading">Total Files</p>
            <p class="title">{{ total_file_count }}</p>
        </div>
    </div>
  </div>
</div>
  
</template>

<style scoped>
    .logo-img {
        width: 40%;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
</style>
