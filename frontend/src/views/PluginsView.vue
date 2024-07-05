<template>
<div class="container column is-10">
    <div class="list has-hoverable-list-items">
        <div v-for="plugin in plugins" class="list-item">
            
            <div class="list-item-image p-2" :title="plugin.type">
            <template v-if="plugin.type == 'unpack'">
                <mdicon name="gift-open" :size="40" />
            </template>
            <template v-else-if="plugin.type == 'unarchive'">
                <mdicon name="archive-arrow-up-outline" :size="40" />
            </template>
            <template v-else-if="plugin.type == 'export'">
                <mdicon name="export" :size="40" />
            </template>
            <template v-else-if="plugin.type == 'identify'">
                <mdicon name="card-search-outline" :size="40" />
            </template>
            <template v-else-if="plugin.type == 'metadata'">
                <mdicon name="database-plus-outline" :size="40" />
            </template>
            <template v-else-if="plugin.type == 'syscall'">
                <mdicon name="console" :size="40" />
            </template>
            <template v-else-if="plugin.type == 'signature'">
                <mdicon name="file-alert" :size="40" />
            </template>
            <template v-else>
                <mdicon name="help-circle-outline" :size="40" />
            </template>
            </div>

            <div class="list-item-content">
                <div class="list-item-title"><router-link :to="{ name: 'PluginSingle', params: { plugin_name: plugin.name }}">{{ plugin.name }}</router-link></div>
                <div class="list-item-description">
                    

                </div>
            </div>
        </div>
        
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
        plugins: [],
        done: false
    }
  },
  props: [],
  mounted() {
    this.getPlugins();
  },
  methods: {
    getPlugins() {

        var self = this;
        api.get_plugin_list(function(result) {
            self.plugins = result;
            self.done = true;
        }, 
        function(status, error){
            console.log('FAILURE!!', status, error);
        });
    }
  }
}
</script>