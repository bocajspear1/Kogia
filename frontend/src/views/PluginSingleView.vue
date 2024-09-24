<script setup>
import PluginPanel from '@/components/plugin/PluginPanel.vue';
import Notifications from '@/components/general/Notifications.vue'
import TabMenuItem from '@/components/menu/TabMenuItem.vue';
import TabMenu from '@/components/menu/TabMenu.vue';
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
                <TabMenu>
                    <template v-slot:main>
                    <TabMenuItem iconname="information" @click="setTab('Info')" :active="current_tab=='Info'">Info</TabMenuItem>
                    <template v-for="display_tab in plugin.display">
                        <TabMenuItem iconname="card" @click="setTab(display_tab.title)" :active="current_tab==display_tab.title">{{ display_tab.title }}</TabMenuItem>
                    </template>
                    </template>
                </TabMenu>
                <div class="card">
                    <div class="card-content">
                        <div v-if="current_tab=='Info'">
                            <p>{{ plugin.docs }}</p>
                            <h2>Options</h2>
                            <ul>
                                <li v-for="option in plugin.options">
                                    <strong>{{ option.name }}</strong>: {{ option.description }}
                                    <template v-if="option.type == 'select'">
                                        , one of {{ option.selections }}
                                    </template>
                                </li>
                                <li v-if="plugin.options.length == 0">
                                    No options
                                </li>
                            </ul>
                        </div>
                        <template v-for="display_tab in plugin.display">
                        <div v-if="current_tab == display_tab.title">
                            <PluginPanel :panel_data="display_tab" :plugin_name="plugin_name"></PluginPanel>
                        </div>
                        </template>
                    </div>
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
import api from '@/lib/api';


export default {
  data() {
    return {
      plugin: {},
      current_tab: "Info",
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
    setTab(new_tab) {
        var self = this;
        self.current_tab = new_tab;
    },
    getPlugin() {
      var self = this;
      this.plugin_name = self.$route.params.plugin_name;
      
      api.get_plugin_data(this.plugin_name, function(data) {
        self.plugin = data;
            
        if (self.plugin.display.length > 0) {
            self.has_display = true;
            // self.current_tab = self.plugin.display[0].title;
        }
        self.done = true;
      },
      function(status, data){
        if (status == 404) {
            self.$refs.notifications.addNotification("error", "Plugin not found");
            self.error = "Plugin not found";
        } else {
            self.$refs.notifications.addNotification("error", data);
            self.error = data;
        }
        
        self.done = true;
        
      });
    }
  }
}
</script>