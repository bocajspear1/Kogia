<script setup>
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue'
import NetworkCommTable from "@/components/host/NetworkCommTable.vue";
</script>
<template>
    <ExecInstDropdown :job_uuid="job_uuid" @execinst_selected="instanceSelected" @execinst_loaded="instancesLoaded" :selected="selected_instance"></ExecInstDropdown>
     
    <div class="notification is-info m-2" v-if="current_instance == null && instance_count > 0">
        Select an execution instance
    </div>
    
    <NetworkCommTable v-if="current_instance != null" :instance_uuid="current_instance.uuid"></NetworkCommTable>
    
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
        done: false,
        netcomm_map: {}
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
