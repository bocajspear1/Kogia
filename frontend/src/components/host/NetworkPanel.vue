<script setup>
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue'
import ProcessDropdown from '@/components/host/ProcessDropdown.vue'
import Paginator from "../general/Paginator.vue";
</script>
<template>
    <ExecInstDropdown :job_uuid="job_uuid" @execinst_selected="instanceSelected" @execinst_loaded="instancesLoaded" :selected="selected_instance"></ExecInstDropdown>
     
    <div class="notification is-info m-2" v-if="netcomms.length == 0">
        Select an execution instance
    </div>
    <template v-if="netcomms.length > 0">
        <table class="table is-striped is-fullwidth">
        <thead>
            <tr>
                <td colspan="4">
                    <Paginator :item_total="netcomm_count" :page_size="page_size" @new_page="onNewPage" :sync_page="netcomm_page"></Paginator>
                </td>
            </tr>
            <tr>
                <th>Protocol</th>
                <th>Source</th>
                <th>Destination</th>
                <th>Data</th>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <td colspan="4">
                    <Paginator :item_total="netcomm_count" :page_size="page_size" @new_page="onNewPage" :sync_page="netcomm_page"></Paginator>
                </td>
            </tr>
        </tfoot>
        <tbody>
            <tr v-for="netcomm in netcomms">
                <td>
                    {{ netcomm.protocol }}
                </td>
                <td>
                    {{ netcomm.src_addr }}:{{ netcomm.src_port }}
                </td>
                <td class="content m-0">
                    {{ netcomm.dest_addr }}:{{ netcomm.dest_port }}
                </td>
                <td class="allow-newlines" >
                    <pre>
{{ netcomm.data }}
                    </pre>
                </td>
            </tr>
        </tbody>
    </table>
    </template>
    
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
        netcomms: [],
        netcomm_page: 1,
        page_size: 30,
        netcomm_count: 0
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
                self.getNetComms();
            },
            function(status, data) {

            }
        )
    },
    instancesLoaded(instance_count){
        this.instance_count = instance_count;
    },
    getNetComms() {
        var self = this;
        api.get_instance_netcomms((self.netcomm_page-1)*self.page_size, self.page_size, self.current_instance['uuid'], function(data) {
            self.netcomms = data['netcomms'];
            self.netcomm_count = data['total'];
        },
        function(status, data) {

        })
        // 
    },
    onNewPage: function(page_num) {
        this.netcomm_page = page_num;
        this.getNetComms();
    }
  }
}
</script>
