<script setup>
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue'
import ProcessDropdown from '@/components/host/ProcessDropdown.vue'
import EventTable from '@/components/host/EventTable.vue'
import ProcessBlock from '@/components/host/ProcessBlock.vue'
import MetadataTable from '../metadata/MetadataTable.vue';
import SyscallTable from '@/components/host/SyscallTable.vue';
</script>
<template>
    <ExecInstDropdown :job_uuid="job_uuid" @execinst_selected="instanceSelected" @execinst_loaded="instancesLoaded"></ExecInstDropdown>
     
    <div class="notification is-info m-2" v-if="instance_count != null && instance_count > 0">
        Select an execution instance
    </div>
    
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";
import time from "@/lib/time";


export default {
  data() {
    return {
        exec_instances: [],
        current_instance: null,
        instance_count: null
    }
  },
  props: ["job_uuid"],
  components: {
    ProcessDropdown,
    ExecInstDropdown
  },
  mounted() {
    
  },
  methods: {
    setTab(new_tab) {
        this.tab = new_tab;
    },
    instanceSelected(new_instance) {
        var self = this;
        
        if ('procDropdown' in self.$refs) {
            self.$refs.procDropdown.clear();
        }
        
        api.get_instance_data(new_instance.uuid,
            function(data) {
                console.log(data);
                self.current_instance = data;
            },
            function(status, data) {

            }
        )
    },
    instancesLoaded(instance_count){
        this.instance_count = instance_count;
    },
    processSelected(new_process) {
        var self = this;
        self.current_process = new_process;
        
    }
  }
}
</script>
