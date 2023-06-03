<script setup>
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue'
import ProcessDropdown from '@/components/host/ProcessDropdown.vue'
import EventTable from '@/components/host/EventTable.vue'
import ProcessBlock from '@/components/host/ProcessBlock.vue'
import MetadataTable from '../metadata/MetadataTable.vue';
</script>
<template>
    <ExecInstDropdown :instances="exec_instances" @execinst_selected="instanceSelected"></ExecInstDropdown>
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
    </div>
     
    <div class="notification is-info m-2" v-else>
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
        exec_instances: [],
        tab: "overview",
        process_list: [],
        current_instance: null,
        metadata_list: [],
        current_process: null
    }
  },
  props: ["job_uuid"],
  components: {
    ProcessDropdown,
    ExecInstDropdown
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
            self.exec_instances = data;
        },
        function(status, data) {

        }
    )
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
        
        api.get_exec_instance_data(new_instance.uuid,
            function(data) {
                console.log(data);
                self.current_instance = data;
            },
            function(status, data) {

            }
        )
    },
    processSelected(new_process) {
        var self = this;
        console.log("hi")
        self.current_process = new_process;
        
    }
  }
}
</script>
