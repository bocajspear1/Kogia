<script setup>

</script>
<template>
    <div class="card">
        <div class="card-content">
            <div class="media">
                <div class="media-content">
                    <h4 class="title is-4">{{ process.path }} ({{ process.pid }})</h4>
                    <h6 class="title is-6">{{ process.command_line }}</h6>
                </div>
            </div>

            <div class="content">
                <div class="level">
                    <div class="level-item has-text-centered">
                        <div>
                            <p class="heading">Child Process Count</p>
                            <p class="title">
                                {{ process.child_processes.length }}  
                            </p>
                        </div>
                    </div>
                    <div class="level-item has-text-centered">
                        <div>
                            <p class="heading">Event Count</p>
                            <p class="title">
                                {{ process.event_count }}
                            </p>
                        </div>
                    </div>
                    <div class="level-item has-text-centered">
                        <div>
                            <p class="heading">Runtime</p>
                            <p class="title">
                                <template v-if="process.end_time - process.start_time != 0">
                                    {{ process.end_time - process.start_time }}
                                </template>
                                <template v-else>
                                    ?
                                </template> 
                            </p>
                        </div>
                    </div>
                </div>
                <p class="title is-5 is-spaced">Libraries</p>
                <ul>
                    <li v-for="library in process.libraries">
                        {{ library  }}
                    </li>
                </ul>
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
  props: ["process"],
  mounted() {
    
  },
  methods: {
    
  }
}
</script>
