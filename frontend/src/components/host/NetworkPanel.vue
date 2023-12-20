<script setup>
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue'
import Paginator from "../general/Paginator.vue";
</script>
<template>
    <ExecInstDropdown :job_uuid="job_uuid" @execinst_selected="instanceSelected" @execinst_loaded="instancesLoaded" :selected="selected_instance"></ExecInstDropdown>
     
    <div class="notification is-info m-2" v-if="current_instance == null && instance_count > 0">
        Select an execution instance
    </div>
    <div class="field is-grouped m-2" v-if="Object.keys(netcomm_stats).length > 0">
        <p class="control">
            <div class="select" v-if="Object.keys(netcomm_stats.addresses).length > 0" >
                <select ref="addressSelect" @change="onAddressSelect">
                    <option selected value="">No address filter</option>
                    <template v-for="(value, address) in netcomm_stats.addresses">    
                    <option :value="address">{{ address }} ({{value}})</option>
                    </template>
                </select>
            </div>
        </p>
        <p class="control">
            <div class="select" v-if="Object.keys(netcomm_stats.ports).length > 0" >
                <select ref="portSelect" @change="onPortSelect">
                    <option selected value="">No port filter</option>
                    <template v-for="(value, port) in netcomm_stats.ports">    
                    <option :value="port">{{ port }} ({{value}})</option>
                    </template>
                </select>
            </div>
        </p>
    </div>
    
    <template v-if="done">
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
            <tr v-if="netcomms.length == 0">
                <td colspan="4">
                    <div class="notification is-warning m-2">
                        No communications matching the filters were found
                    </div>
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
        instance_count: null,
        netcomms: [],
        netcomm_page: 1,
        page_size: 30,
        netcomm_count: 0,
        netcomm_stats: {},
        address_filter: "",
        port_filter: "",
        done: false
    }
  },
  props: ["job_uuid", "selected_instance"],
  emits: ["instance_selected"],
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
        
        api.get_instance_data(new_instance.uuid,
            function(data) {
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
        api.get_instance_netcomms((self.netcomm_page-1)*self.page_size, self.page_size, self.current_instance['uuid'],  
                                  self.address_filter, self.port_filter, function(data) {
            self.netcomms = data['netcomms'];
            self.netcomm_count = data['total'];
            self.netcomm_stats = data['statistics'];
            self.done = true;
        },
        function(status, data) {

        })
        // 
    },
    onNewPage: function(page_num) {
        console.log(this.netcomm_page, page_num);
        this.netcomm_page = page_num;
        
        this.getNetComms();
    },
    onAddressSelect: function(event) {
        this.address_filter = event.target.value;
        this.netcomm_page = 1;
        this.getNetComms();
    },
    onPortSelect: function(event) {
        this.port_filter = event.target.value;
        this.netcomm_page = 1;
        this.getNetComms();
    }
  }
}
</script>
