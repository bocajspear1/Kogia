<script setup>
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue'
import ProcessDropdown from '@/components/host/ProcessDropdown.vue'
import EventTable from '@/components/host/EventTable.vue'
import ProcessBlock from '@/components/host/ProcessBlock.vue'
import MetadataTable from '../metadata/MetadataTable.vue';
import SyscallTable from '@/components/host/SyscallTable.vue';

import TabMenuItem from '@/components/menu/TabMenuItem.vue';
import TabMenu from '@/components/menu/TabMenu.vue';

import Image from '@/components/general/Image.vue';
</script>
<template>
    <ExecInstDropdown :job_uuid="job_uuid" @execinst_selected="instanceSelected" @execinst_loaded="instancesLoaded" :selected="selected_instance"></ExecInstDropdown>
    <div class="m-2" v-if="current_instance != null">
        <TabMenu>
            <template v-slot:main>
            <TabMenuItem iconname="file-cog" @click="instanceTabSelected('processes')" :active="instance_tab=='processes'">Processes ({{ current_instance.process_count }})</TabMenuItem>
            <TabMenuItem iconname="monitor-screenshot" @click="instanceTabSelected('screenshots')" :active="instance_tab=='screenshots'">Screenshots</TabMenuItem>
            <TabMenuItem iconname="table-multiple" @click="instanceTabSelected('metadata')" :active="instance_tab=='metadata'">Metadata</TabMenuItem>
            </template>
        </TabMenu>
        <div class="card">
            <div class="card-content">
                <template v-if="instance_tab=='screenshots'">
                    <template v-for="thumbnail in thumbnails">
                        <Image :base64Data="thumbnail.image_data" :name="thumbnail.name" @click="onThumbClick" :clickable="true"></Image>
                    </template>
                    
                </template>
                <template v-if="instance_tab=='metadata'">
                    <MetadataTable :instance_uuid="current_instance.uuid"></MetadataTable>
                </template>
                <template v-if="instance_tab=='processes'">
                    <span class="m-2 is-vcentered" >
                        <ProcessDropdown ref="procDropdown" :processes="current_instance.processes" @process_selected="processSelected"></ProcessDropdown>
                    </span>
                    <div v-if="current_process != null">
                        <div class="tabs">
                            <ul>
                                <li :class="process_tab == 'overview' ? 'is-active' : ''"><a @click="setProcessTab('overview')">Overview</a></li>
                                <li :class="process_tab == 'metadata' ? 'is-active' : ''"><a @click="setProcessTab('metadata')">Metadata</a></li>
                                <li :class="process_tab == 'events' ? 'is-active' : ''"><a @click="setProcessTab('events')">Events</a></li>
                                <li :class="process_tab == 'syscalls' ? 'is-active' : ''"><a @click="setProcessTab('syscalls')">Syscalls</a></li>
                            </ul>
                        </div>
                        <EventTable :process_uuid="current_process.uuid" v-if="process_tab == 'events'"></EventTable>
                        <ProcessBlock :process="current_process" v-if="process_tab == 'overview'"></ProcessBlock>
                        <MetadataTable :process_uuid="current_process.uuid" v-if="process_tab == 'metadata'"></MetadataTable>
                        <SyscallTable :process_uuid="current_process.uuid" v-if="process_tab == 'syscalls'"></SyscallTable>
                    </div>
                </template>

            </div>
        </div>
        
        
    </div>
    <div v-else class="notification is-info m-2" v-if="instance_count != null && instance_count > 0">
        Select an execution instance
    </div>
    <div class="modal" ref="fullimage">
        <div class="modal-background" @click="closeModal"></div>
        <div class="modal-content" v-if="full_image != null">
            <Image :base64Data="full_image.image_data" :name="full_image.name"></Image>
        </div>
        <button class="modal-close is-large" aria-label="close" @click="closeModal"></button>
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
        instance_tab: "processes",
        process_tab: "overview",
        process_list: [],
        current_instance: null,
        metadata_list: [],
        current_process: null,
        instance_count: null,
        thumbnails: [],
        full_image: null
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
    setProcessTab(new_process_tab) {
        this.process_tab = new_process_tab;
    },
    instanceTabSelected(new_instance_tab) {
        this.instance_tab = new_instance_tab;
        if (this.instance_tab == "screenshots") {
            this.updateThumbnails();
        } else if (this.instance_tab == "processes") {
            this.current_process = null;
        }
    },
    updateThumbnails() {
        console.log("thumbnails")
        var self = this;
        self.thumbnails = [];

        // TODO: Rapidly clicking before all images are loaded can cause duplicates
        function loadNext(i) {
            if (i >= self.current_instance.screenshots.length) {
                return;
            }
            var screenshot_name = self.current_instance.screenshots[i];
            api.get_instance_thumbnail(self.current_instance.uuid, screenshot_name, function(data) {
                self.thumbnails.push(data);
                loadNext(i+1);
            },
            function(status, data) {

            })
        }
        loadNext(0);
        
        
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
                self.instance_tab = 'processes';
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
        
    },
    onThumbClick(image_name) {
        var self = this;
        self.full_image = null;
        api.get_instance_screenshot(self.current_instance.uuid, image_name.replace("-t", ""), function(data) {
            self.full_image = data;
            self.$refs.fullimage.classList.add('is-active');
        },
        function(status, data) {

        })
    },
    closeModal() {
        var self = this;
        self.$refs.fullimage.classList.remove('is-active');
    }
  }
}
</script>
