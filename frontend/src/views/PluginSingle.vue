<script setup>
import DynamicPanel from '@/components/DynamicPanel.vue'
import Notifications from '@/components/Notifications.vue'
</script>

<template>
<div class="container column is-10">
    <Notifications ref="notifications"></Notifications>
    <div class="card" v-if="done && !error">
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
                            <DynamicPanel :panel_data="display_tab" :plugin_name="plugin_name"></DynamicPanel>
                        </div>
                    </template>
                </div>
            </div>
        </div>
        <footer class="card-footer">
            <a href="#" class="card-footer-item">Refresh</a>
        </footer>
    </div>
    <div class="p-3" v-else-if="error">
        {{ error }}
    </div>
    <div class="p-3" v-else>
        <progress class="progress is-small is-primary" max="100">50%</progress>
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
      plugin: {},
      current_tab: "",
      has_display: false,
      plugin_name: "",
      done: false,
      error: null,
    }
  },
  mounted() {
    this.getPlugin();
  },
  methods: {
    getPlugin() {
      var self = this;
      this.plugin_name = self.$route.params.plugin_name;
      
      axios.get("/api/v1/plugin/" + this.plugin_name + "/info").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                self.plugin = resp_data['result'];
                
                if (self.plugin.display.length > 0) {
                    self.has_display = true;
                    self.current_tab = self.plugin.display[0].title;
                }
                self.done = true;
            } else {
                self.$refs.notifications.addNotification("error", resp_data['error']);
                self.done = true;
                self.error = resp_data['error'];
            }
            
        }).catch(function(resp){
           
            if (resp['response']['status'] == 404) {
                self.$refs.notifications.addNotification("error", "Plugin not found");
                self.error = "Plugin not found";
            } else {
                console.log(resp);
                self.$refs.notifications.addNotification("error", resp);
                self.error = resp;
            }
            self.done = true;
            
        });
    }
  }
}
</script>