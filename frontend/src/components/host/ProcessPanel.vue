<script setup>
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue'
import ProcessDropdown from '@/components/host/ProcessDropdown.vue'
</script>
<template>
    <ExecInstDropdown :instances="exec_instances" @execinst_selected="instanceSelected"></ExecInstDropdown>
    <span v-if="current_instance != null" class="m-2 is-vcentered" >
        <ProcessDropdown :processes="current_instance.processes"></ProcessDropdown>
    </span>
    <div class="tabs">
        <ul>
            <li :class="tab == 'overview' ? 'is-active' : ''"><a @click="setTab('overview')">Overview</a></li>
            <li :class="tab == 'events' ? 'is-active' : ''"><a @click="setTab('events')">Events</a></li>
            <li :class="tab == 'syscalls' ? 'is-active' : ''"><a @click="setTab('syscalls')">Syscalls</a></li>
        </ul>
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
        tab: "",
        process_list: [],
        current_instance: null
    }
  },
  props: ["job_uuid"],
  mounted() {
    var self = this;
    api.get_job_exec_instances(self.job_uuid, 
        function(data) {
            for (var i in data) {
                var item = data[i];

                item['end_time'] = time.seconds_to_string(item['end_time']);
                item['start_time'] = time.seconds_to_string(item['start_time']);
            }
            self.exec_instances = data;
        },
        function(status, data) {

        }
    )
  },
  methods: {
    setTab(new_tab) {

    },
    instanceSelected(new_instance) {
        var self = this;
        api.get_exec_instance_data(new_instance.uuid,
            function(data) {
                console.log(data);
                self.current_instance = data;
            },
            function(status, data) {

            }
        )
    }
  }
}
</script>
