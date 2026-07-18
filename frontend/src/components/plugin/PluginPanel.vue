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
        console.log(item)
        var type_obj = null;
        if (item['type'] == 'databar') {
            type_obj = shallowRef(GenericDataBar);
        } else if (item['type'] == 'table') {
            type_obj = shallowRef(GenericDataBar);
        }

        var id = self.plugin_name + "." + item['action'];
        var new_item = {
            "type": type_obj,
            "loadon": item['on'],
            "id": id, 
            "data": null
        }

        this.panel_contents.push(new_item);

        if (item['on'] == 'load') {

            var load_func = function(action_id, result) {

                for (var j in self.panel_contents) {
                    console.log(action_id)
                    if (self.panel_contents[j]['id'] == action_id) {
                        self.panel_contents[j]['data'] = result;
                    }
                }

                console.log(self.panel_contents)

            };
            load_func.id = id;
            api.get_plugin_action(self.plugin_name, item['action'], load_func, function(status, error) {
            console.log('FAILURE!!', status, error);
            })
        }

        
    }


    },
    methods: {

    }
}
</script>
