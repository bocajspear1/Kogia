<script setup>
import GenericDropdown from '@/components/generic/GenericDropdown.vue'
</script>
<template>
<div class="notification is-warning m-2" v-if="instances.length == 0 && loaded == true">
    No execution instances for this job
</div>
<GenericDropdown @item_selected="onSelect" ref="intDropdown" v-if="instances.length > 0 && loaded == true"  :initSelect="selected">
    <template v-slot:selected="selected">
        <mdicon name="application-braces" :size="25" />&nbsp;
        <span v-if="selected.selected == null" >
            Select Execution Instance
        </span>
        <span v-if="selected.selected != null">
            {{ selected.selected.exec_module }} (Finished: {{ selected.selected.end_time_relative }}, Duration: {{ selected.selected.duration }})
        </span>
    </template>
    <template v-slot:dropcontent="dropcontent">
        <template v-if="instances.length != 0">
        <a v-for="instance in instances" class="dropdown-item" @click="dropcontent.onSelect(instance)">
            <mdicon name="microsoft-windows" :size="25" v-if="instance.run_os=='windows'"/>
            <mdicon name="file-cog" :size="25" v-if="instance.run_os=='linux'"/>
            {{ instance.exec_module }} (Finished: {{ instance.end_time_relative }}, Duration: {{ instance.duration }})
        </a>
        </template>
        <template v-if="instances.length == 0">
            <span class="dropdown-item">No Instances</span>
        </template>
    </template>
</GenericDropdown>
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";
import time from "@/lib/time";

export default {
  data() {
    return {
        current_instance: null,
        instances: [],
        loaded: false
    }
  },
  emits: ["execinst_selected", "execinst_loaded"],
  props: {
    job_uuid: String,
    selected: null
  },
  mounted() {
    var self = this;
    api.get_job_exec_instances(self.job_uuid, 
        function(data) {
            for (var i in data) {
                data[i] = time.add_pretty_times(data[i], ['start_time', 'end_time'], [['start_time', 'end_time', 'duration']]);
            }
            self.instances = data;
            self.loaded = true;
            self.$emit('execinst_loaded', self.instances.length);
            console.log(self.selected);
            if (self.selected) {
                self.current_instance = self.selected;
            }
        },
        function(status, data) {

        }
    )
    
  },
  unmounted() {
    
  },
  methods: {
    onSelect(instance) {
        this.current_instance = instance;
        this.$emit('execinst_selected', instance);
    }
  }
}
</script>