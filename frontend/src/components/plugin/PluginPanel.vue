<template>
    <div v-for="(schema, index) in panel_contents" :key="index">
      <component
        :key="index"
        :is="schema.type"
        :loadon="schema.loadon"
        :plugin_name="schema.plugin_name"
        :data="schema.data"
      >
      </component>
    </div>
</template>

<style scoped>

</style>

<script>
import { shallowRef,  ref, computed } from 'vue'
import GenericDataBar from '@/components/generic/GenericDataBar.vue'
import GenericList from '@/components/generic/GenericList.vue'
import GenericTable from '@/components/generic/GenericTable.vue'

import api from "@/lib/api";

export default {
  data() {
    return {
      panel_contents: []
    }
  },
  props: ["panel_data", "plugin_name"],
  mounted() {
    var self = this;

    for (var i in this.panel_data.items) {
        var item = this.panel_data.items[i];
        var type_obj = null;
        if (item['type'] == 'databar') {
          type_obj = shallowRef(GenericDataBar);
        } else if (item['type'] == 'table') {
          type_obj = shallowRef(GenericDataBar);
        }

        var new_item = {
          "type": type_obj,
          "loadon": item['on'],
          "plugin_name": self.plugin_name, 
          "data": null
        }

        this.panel_contents.push(new_item);

        if (item['on'] == 'load') {
            api.get_plugin_action(self.plugin_name, item['action'], function(result) {

            for (var j in self.panel_contents) {
                if (self.panel_contents[j]['plugin_name'] == self.plugin_name) {
                    self.panel_contents[j]['data'] = result;
                }
            }

            console.log(self.panel_contents)

            }, function(status, error) {
            console.log('FAILURE!!', status, error);
            })
        }

        
    }
    
    
  },
  methods: {
    
  }
}
</script>
