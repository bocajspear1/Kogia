<script setup>
import GenericDropdown from '@/components/generic/GenericDropdown.vue'
</script>
<template>
<div class="notification is-warning m-2" v-if="instances.length == 0 && loaded == true">
    No execution instances for this job
</div>
<GenericDropdown @item_selected="onSelect" ref="intDropdown" v-if="instances.length > 0 && loaded == true">
    <template v-slot:selected="selected">
        <mdicon name="application-braces" :size="25" />&nbsp;
        <span v-if="selected.selected == null" >
            Select Execution Instance
        </span>
        <span v-if="selected.selected != null">
            {{ selected.selected.exec_module }} (Finished: {{ selected.selected.end_time }}, Duration: {{ selected.selected.duration }})
        </span>
    </template>
    <template v-slot:dropcontent="dropcontent">
        <template v-if="instances.length != 0">
        <a v-for="instance in instances" class="dropdown-item" @click="dropcontent.onSelect(instance)">
            <mdicon name="microsoft-windows" :size="25" v-if="instance.run_os=='windows'"/>
            <mdicon name="file-cog" :size="25" v-if="instance.run_os=='linux'"/>
            {{ instance.exec_module }} (Finished: {{ instance.end_time }}, Duration: {{ instance.duration }})
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
  },
  mounted() {
    var self = this;
    api.get_job_exec_instances(self.job_uuid, 
        function(data) {
            for (var i in data) {
                var item = data[i];

                var end_time_num = item['end_time'];
                item['end_time'] = time.seconds_to_string(end_time_num);
                var start_time_num = item['start_time'];
                item['start_time'] = time.seconds_to_string(start_time_num);
                item['duration'] = time.seconds_duration(start_time_num, end_time_num);
            }
            self.instances = data;
            self.loaded = true;
            self.$emit('execinst_loaded', self.instances.length);
        },
        function(status, data) {

        }
    )
    
  },
  unmounted() {
    
  },
  methods: {
    onSelect(file) {
        console.log(file);
        this.current_instance = file;
        this.$emit('execinst_selected', file);
    }
  }
}
</script>