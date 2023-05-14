<template>
    <div v-for="(schema, index) in panel_contents" :key="index">
      <component
        :key="index"
        :is="schema.type"
        :loadon="schema.loadon"
        :plugin_name="schema.plugin_name"
        :action="schema.action"
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
        this.panel_contents.push({
          "type": type_obj,
          "loadon": item['on'],
          "plugin_name": self.plugin_name, 
          "action": item['action']
        });
    }
    
    console.log(this.panel_contents)
  },
  methods: {
    
  }
}
</script>
