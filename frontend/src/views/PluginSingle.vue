<script setup>

</script>

<template>
    <div class="card">
    <header class="card-header">
        <p class="card-header-title">
            {{ plugin.name }}
        </p>
    </header>
    <div class="card-content">
        <div class="content">
            <div v-if="has_display">
                <div class="tabs">
                    <ul>
                        <template v-for="display_tab in plugin.display">
                            <li v-if="current_tab == display_tab.title" class="is-active"><a>{{ display_tab.title }}</a></li>
                            <li v-else><a>{{ display_tab.title }}</a></li>
                        </template>
                    </ul>
                </div>
                <template v-for="display_tab in plugin.display">
                    <div v-if="current_tab == display_tab.title">

                    </div>
                </template>
            </div>
        </div>
    </div>
    <footer class="card-footer">
        <a href="#" class="card-footer-item">Refresh</a>
    </footer>
    </div>
    
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      plugin: {},
      current_tab: "",
      has_display: false
    }
  },
  mounted() {
    this.getPlugin();
  },
  methods: {
    getPlugin() {
      var self = this;
      var plugin_name = self.$route.params.plugin_name;
      
      axios.get("/api/v1/plugin/" + plugin_name + "/info").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                self.plugin = resp_data['result'];
                console.log(self.plugin)
                if (self.plugin.display.length > 0) {
                    self.has_display = true;
                    self.current_tab = self.plugin.display[0].title;
                }
                self.done = true;
            }
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>