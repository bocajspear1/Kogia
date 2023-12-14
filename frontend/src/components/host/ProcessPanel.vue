<script setup>
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue'
import ProcessDropdown from '@/components/host/ProcessDropdown.vue'
import EventTable from '@/components/host/EventTable.vue'
import ProcessBlock from '@/components/host/ProcessBlock.vue'
import MetadataTable from '../metadata/MetadataTable.vue';
import SyscallTable from '@/components/host/SyscallTable.vue';
</script>
<template>
    <ExecInstDropdown :job_uuid="job_uuid" @execinst_selected="instanceSelected" @execinst_loaded="instancesLoaded" :selected="selected_instance"></ExecInstDropdown>
    <span v-if="current_instance != null" class="m-2 is-vcentered" >
        <ProcessDropdown ref="procDropdown" :processes="current_instance.processes" @process_selected="processSelected"></ProcessDropdown>
    </span>
    <div v-if="current_process != null">
        <div class="tabs">
            <ul>
                <li :class="tab == 'overview' ? 'is-active' : ''"><a @click="setTab('overview')">Overview</a></li>
                <li :class="tab == 'metadata' ? 'is-active' : ''"><a @click="setTab('metadata')">Metadata</a></li>
                <li :class="tab == 'events' ? 'is-active' : ''"><a @click="setTab('events')">Events</a></li>
                <li :class="tab == 'syscalls' ? 'is-active' : ''"><a @click="setTab('syscalls')">Syscalls</a></li>
            </ul>
        </div>
        <EventTable :process_uuid="current_process.uuid" v-if="tab == 'events'"></EventTable>
        <ProcessBlock :process="current_process" v-if="tab == 'overview'"></ProcessBlock>
        <MetadataTable :process_uuid="current_process.uuid" v-if="tab == 'metadata'"></MetadataTable>
        <SyscallTable :process_uuid="current_process.uuid" v-if="tab == 'syscalls'"></SyscallTable>
    </div>
     
    <div v-else class="notification is-info m-2" v-if="instance_count != null && instance_count > 0">
        Select an execution instance and process
    </div>
    
</template>

<style scoped>

</style>

<script>
import time from "@/lib/time";
import api from "@/lib/api";

export default {
  data() {
    return {
        tab: "overview",
        process_list: [],
        current_instance: null,
        metadata_list: [],
        current_process: null,
        instance_count: null
    }
  },
  props: ["job_uuid", "selected_instance"],
  emits: ["instance_selected"],
  components: {
    ProcessDropdown,
    ExecInstDropdown
  },
  mounted() {
    var self = this;
    if (self.selected_instance != null && self.selected_instance != undefined) {
        self.current_instance = self.selected_instance;
        self.instanceSelected(self.current_instance);
    }
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
                self.$emit('instance_selected', self.current_instance);
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
        console.log("hi")
        self.current_process = new_process;
        
    }
  }
}
</script>
