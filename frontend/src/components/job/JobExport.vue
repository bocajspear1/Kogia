<script setup>
import Paginator from "../general/Paginator.vue";
import Notifications from '@/components/general/Notifications.vue';
import DynamicOptions from '@/components/dynamic/DynamicOptions.vue';
import FileMultiSelectList from '@/components/file/FileMultiSelectList.vue';
import JobExportExecInst from '@/components/job/JobExportExecInst.vue';
import JobExportNetComm from '@/components/job/JobExportNetComm.vue';
import MetadataViewer from '@/components/metadata/MetadataViewer.vue';
import TabMenuItem from '@/components/menu/TabMenuItem.vue';
import TabMenu from '@/components/menu/TabMenu.vue';
</script>

<template>
    <div class="container p-4">
        <Notifications ref="notifications"></Notifications>
        <div class="field is-grouped p-4">
            <div class="control">
                <div class="select is-fullwidth">
                    <select ref="exportPluginSelect" @change="onSelect">
                        <option selected value="">Select Export Plugin</option>
                        <template v-for="export_plugin in export_plugins">    
                        <option :value="export_plugin.name">{{ export_plugin.name }}</option>
                        </template>
                    </select>
                </div>
            </div>
            <div class="control">
                <button class="button is-link" @click="runExport">Export</button>
            </div>
        </div>
        <div v-if="selected_plugin != null">
            <div class="mt-2">
                <TabMenu>
                    <template v-slot:main>
                    <TabMenuItem iconname="cog" @click="setProcessTab('options')" :active="current_tab=='options'">Options</TabMenuItem>
                    <TabMenuItem iconname="file-cog" @click="setProcessTab('processes')" 
                        :active="current_tab=='processes'" v-if="selected_plugin.config['show_events'] != false || selected_plugin.config['show_syscalls'] != false">Processes</TabMenuItem>
                    <TabMenuItem iconname="server-network" @click="setProcessTab('networking')" 
                        :active="current_tab=='networking'" v-if="selected_plugin.config['show_network'] != false">Networking</TabMenuItem>
                    <TabMenuItem iconname="file" @click="setProcessTab('files')" 
                        :active="current_tab=='files'" v-if="selected_plugin.config['show_files'] != false">Files</TabMenuItem>
                    <TabMenuItem iconname="table-multiple" @click="setProcessTab('metadata')" 
                        :active="current_tab=='metadata'" v-if="selected_plugin.config['show_metadata'] != false">Metadata</TabMenuItem>
                    <TabMenuItem iconname="file-chart" @click="setProcessTab('reports')" 
                        :active="current_tab=='reports'"  v-if="selected_plugin.config['show_reports'] != false">Reports</TabMenuItem>
                    </template>
                </TabMenu>
            </div>

            <div class="card" v-show="current_tab == 'options'">
                <div class="content p-4">
                    <div class="field" v-if="selected_plugin.config['show_signatures'] != false">
                        <div class="control">
                            <label class="checkbox">
                                <input type="checkbox" v-model="include_signatures">
                                Include signatures
                            </label>
                        </div>
                        
                    </div>
                    <DynamicOptions :options="selected_plugin.options" @onOptionChange="onOptionChange"></DynamicOptions>
                </div>
            </div>
            <div class="card" v-show="current_tab == 'processes'">
                <div class="content p-4">
                    <div class="field">
                        <div class="control" v-if="selected_plugin.config['show_events'] != false">
                            <label class="checkbox">
                                <input type="checkbox" v-model="include_events">
                                Include process events
                            </label>
                        </div>
                        <div class="control" v-if="selected_plugin.config['show_syscalls'] != false">
                            <label class="checkbox">
                                <input type="checkbox" v-model="include_syscalls">
                                Include process syscalls
                            </label>
                        </div>
                        <JobExportExecInst v-if="include_events || include_syscalls" :exec_instances="exec_instances" 
                            :include_syscalls="include_syscalls" :include_events="include_events"
                            :all_checked="true" @eventFilterUpdate="onEventFilterUpdate"></JobExportExecInst>
                    </div>
                </div>
                
            </div>
            <div class="card"  v-show="current_tab == 'networking'">
                <div class="content p-4">
                    <div class="field">
                        <div class="control">
                            <label class="checkbox">
                                <input type="checkbox" v-model="include_netcomms">
                                Include network communications
                            </label>
                        </div>
                        <JobExportNetComm :exec_instances="exec_instances" @netCommFilterUpdate="onNetCommFilterUpdate" :all_checked="true"></JobExportNetComm>
                    </div>
                </div>
            </div>
            <div class="card"  v-show="current_tab == 'files'">
                <div class="content p-4">
                    <div class="field">
                        <div class="control">
                            <label class="checkbox">
                                <input type="checkbox" v-model="include_files">
                                Include files
                            </label>
                        </div>
                    </div>

                    <FileMultiSelectList v-if="files != null && include_files" :toggle="false" :files="files" :all_checked="true" @file_checked="fileChecked"></FileMultiSelectList>
                    <div class="field">
                        <div class="control">
                            <label class="checkbox">
                                <input type="checkbox" v-model="options['add_file_metadata']">
                                Add metadata to files
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card" v-show="current_tab == 'metadata'">
                <div class="content p-4">
                    <div class="field">
                        <div class="control">
                            <label class="checkbox">
                                <input type="checkbox" v-model="include_metadata">
                                Include metadata
                            </label>
                        </div>
                    </div>

                    <MetadataViewer v-if="include_metadata" :job="job" :selectable="true" @metadataSelected="onMetadataSelected"></MetadataViewer>
                </div>
            </div>
            <div class="card" v-show="current_tab == 'reports'">
                <div class="content p-4">
                    <div class="field">
                        <div class="control">
                            <label class="checkbox">
                                <input type="checkbox" v-model="include_reports">
                                Include reports
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            
        </div>
        <iframe ref="download_iframe" style="display:none;"></iframe>
        
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
        export_plugins: [],
        exec_instances: [],
        event_filter: {},
        syscall_filter: {},
        netcomm_filter: {},
        current_tab: "options",
        options: {
            "add_file_metadata": false
        },
        selected_plugin: null,
        include_signatures: true,
        include_events: true,
        include_syscalls: false,
        include_netcomms: true,
        include_metadata: false,
        include_files: true,
        include_reports: true,
        add_metadata_files: false,
    }
  },
  props: ["job", "files"],
  mounted() {
    this.getExportPlugins();
    this.getExecInstances();
  },
  methods: {
    getExportPlugins() {

        var self = this;

        api.get_plugin_list_type("export", function(data){
            self.export_plugins = data;
        }, function(status, data) {

        });
    },
    onOptionChange(new_options) {
        this.options = Object.assign(this.options, new_options);
    },
    onSelect: function(event) {
        if (event.target.value != "" && event.target.value != this.selected_plugin) {
            for (var i in this.export_plugins) {
                var plugin = this.export_plugins[i];
                if (plugin.name == event.target.value) {
                    this.selected_plugin = plugin;
                }
            } 
        }
    },
    fileChecked(file_list) {
        this.selected_files = file_list;
    },
    getExecInstances() {
        var self = this;
        api.get_job_exec_instances(self.job.uuid, 
            function(data) {
                for (var i in data) {
                    data[i] = time.add_pretty_times(data[i], ['start_time', 'end_time'], [['start_time', 'end_time', 'duration']]);
                }
                self.exec_instances = data;
            },
            function(status, data) {

            }
        )
    },
    setProcessTab(new_tab) {
        this.current_tab = new_tab;
    },
    metadataSelected(metadata_selected) {
        this.metadata_selected = metadata_selected;
    },
    onMetadataSelected(metadata_type, key, value) {
        console.log(metadata_type, key, value)
    },
    onEventFilterUpdate(new_filter) {
        
        this.event_filter = new_filter['events'];
        this.syscall_filter = new_filter['syscalls'];
        console.log(this.event_filter)
    },
    onNetCommFilterUpdate(new_filter) {
        this.netcomm_filter = new_filter;
        // this.syscall_filter = new_filter['syscalls'];
    },
    runExport() {
        var self = this;

        var export_data = {
            options: self.options,
            events: {},
            syscalls: {},
            network: {},
            files: [],
            reports: []
        }

        if (this.include_events) {
            export_data.events = this.event_filter;
        }

        if (this.include_syscalls) {
            export_data.syscalls = this.syscall_filter;
        }

        if (this.include_netcomms) {
            export_data.network = this.netcomm_filter;
        }

        if (this.include_files) {
            for (var i in this.files) {
                export_data['files'].push(this.files[i].uuid)
            }
        }  

        if (this.include_reports) {

        } 

        
        api.do_job_export(self.job.uuid, self.selected_plugin.name, export_data, 
        function(data) {
            var download_token = data['download_token'];
            var export_uuid = data['export_uuid'];
            self.$refs.download_iframe.src = '/api/v1/export/' + export_uuid + "/download?download_token=" + download_token;
        }, function(status, data) {
            self.$refs.notifications.addNotification("error", "Export Error: " + data);
        })
    }
  }
}
</script>