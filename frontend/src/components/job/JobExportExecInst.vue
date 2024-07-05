<script setup>
import EventTable from '@/components/host/EventTable.vue'
import ProcessNodes from '@/components/host/ProcessNodes.vue'
import ProcessItem from '@/components/job/JobExportProcessItem.vue'
import TabMenuItem from '@/components/menu/TabMenuItem.vue';
import TabMenu from '@/components/menu/TabMenu.vue';
</script>
<template>
    <div class="list">
        <div v-for="exec_instance in exec_instances" class="list-item" :ref="exec_instance.uuid">
            <div class="list-item-image p-2">
                <label class="checkbox m-4">
                    <input type="checkbox" @input="instanceCheckClicked(exec_instance.uuid, $event.target.checked)" :checked="all_checked">
                </label>
                <mdicon name="application-braces" :size="35"/>
            </div>
            <div class="list-item-content">
                <div class="list-item-title">
                    <h2 class="title is-h2">{{ exec_instance.exec_module }} ({{ exec_instance.duration }})</h2>
                </div>
                <div class="list-item-description">
                    <div class="field is-grouped">
                        <p class="control">
                            <div class="select">
                                <select @change="onIncludeProcessSelect(exec_instance, $event.target.value)">
                                    <option selected value="none">Include NO processes</option>
                                    <option value="all_nodata" v-if="include_syscalls && include_events">Include ALL processes, NO events, NO syscalls</option>
                                    <option value="all_noevents" v-if="include_syscalls && include_events">Include ALL processes, NO events, ALL syscalls</option>
                                    <option value="all_noevents" v-if="!include_syscalls && include_events">Include ALL processes, NO events</option>
                                    <option value="all_nosyscalls" v-if="include_syscalls && include_events">Include ALL processes, ALL events, NO syscalls</option>
                                    <option value="all_nosyscalls" v-if="include_syscalls && !include_events">Include ALL processes, NO syscalls</option>
                                    <option value="all" v-if="include_syscalls && include_events">Include ALL processes, ALL events, ALL syscalls</option>
                                    <option value="all" v-if="!include_syscalls && include_events">Include ALL processes, ALL events</option>
                                    <option value="all" v-if="include_syscalls && !include_events">Include ALL processes, ALL syscalls</option>
                                    <option value="some">Include SOME processes</option>
                                </select>
                            </div>
                        </p>
                        <p class="control">
                            
                        </p>
                    </div>

                    <div class="card" v-show="inserted == 'some'">
                        <header class="card-header has-background-info-dark has-text-link-light">
                            <span class="card-header-title has-text-link-light">Process list</span>
                            <button class="card-header-icon" @click="toggleProcessList(exec_instance.uuid)">
                                <span class="icon">
                                    <mdicon name="chevron-down" :size="30" v-if="show_processes_map[exec_instance.uuid]" />
                                    <mdicon name="chevron-up" :size="30" v-if="!show_processes_map[exec_instance.uuid]" />
                                </span>
                            </button>
                        </header>
                        <div class="card-content has-background-info-light" v-show="show_processes_map[exec_instance.uuid] && exec_instance_data[exec_instance.uuid] != undefined" >
                            <div class="content is-vcentered" v-if="exec_instance_data[exec_instance.uuid] != undefined">
                                <ProcessNodes v-show="show_processes_map[exec_instance.uuid]" :processes="exec_instance_data[exec_instance.uuid].processes" 
                                    @process_checked="onProcessChecked" :selectable="true"></ProcessNodes>
                            </div>
                        </div>
                        
                    </div>

                    <template v-if="exec_instance.uuid in proc_event_map">

                    <div v-for="process_uuid in Object.keys(proc_event_map[exec_instance.uuid])">
                        <ProcessItem :process="process_map[process_uuid]" 
                            @selectUpdated="onProcessSelect" 
                            @eventChecked="onEventChecked" 
                            @syscallChecked="onSyscallChecked" 
                            v-if="process_uuid != '*'"></ProcessItem>
                    </div>
                    <div class="notification is-info m-3" v-if="Object.keys(proc_event_map[exec_instance.uuid]).length == 0">
                        Select one or more processes from process list
                    </div>

                    </template>
                </div>
            </div>
        </div>
    </div>

    <div class="ml-6" v-show="inserted != 'none'">
        <TabMenu>
            <template v-slot:main>
            <TabMenuItem iconname="clock" @click="setProcessTab('events')" :active="current_tab=='events'"  v-if="include_events">Events ({{ getEventCount }})</TabMenuItem>
            <TabMenuItem iconname="card-search" @click="setProcessTab('syscalls')" :active="current_tab=='syscalls'" v-if="include_syscalls">Syscalls</TabMenuItem>
            </template>
        </TabMenu>


        <table class="table is-striped is-fullwidth m-5" v-if="current_tab=='events'">
            <thead>
                <tr>
                    <th>Process</th>
                    <th>Event Type</th>
                    <th>Information</th>
                    <th>Data</th>
                    <th>Success</th>
                </tr>
            </thead>
            <tfoot>
                <tr>
                
                </tr>
            </tfoot>

            <tbody>
                <template v-for="(inst_procs, inst_uuid) in proc_event_map">
                    <template v-for="(proc_events, process_uuid) in inst_procs">
                    <tr v-if="proc_event_map[inst_uuid][process_uuid].length == 0">
                        <td v-if="process_uuid != '*'">
                            {{ process_map[process_uuid].path }}
                        </td>
                        <td v-else>
                            ALL processes
                        </td>
                        <td colspan="4" class="has-text-centered"><strong>No events</strong></td>
                    </tr>
                    <tr v-for="event in proc_event_map[inst_uuid][process_uuid]">
                        <template v-if="event == '*'">
                            <td v-if="process_uuid != '*'">
                                {{ process_map[process_uuid].path }}
                            </td>
                            <td v-else>
                                ALL processes
                            </td>
                            <td colspan="4" class="has-text-centered"><strong>ALL events</strong></td>
                        </template>
                        <template v-else>
                            <td>
                                {{ event.process.path }}
                            </td>
                            <td>
                                {{ event.key }}
                            </td>
                            <td class="allow-newlines m-0 limit-data">
                                <ul class="m-0 limit-data">
                                    <li v-if="event.src != null && event.src != ''">
                                        <strong>Source:</strong> {{ event.src }}
                                    </li>
                                    <li v-if="event.dest != null && event.dest != ''">
                                        <strong>Destination:</strong> {{ event.dest }}
                                    </li>
                                </ul>
                            </td>
                            <td class="allow-newlines limit-data" >
                                {{ event.data }}
                            </td>
                            <td>
                                {{ event.success }}
                            </td>
                        </template>
                        
                    </tr>
                    </template>
                
                </template>
                
            </tbody>
        </table>

        <table class="table is-striped is-fullwidth m-5" v-if="current_tab=='syscalls'">
            <thead>
                <tr>
                    <th>Process</th>
                    <th>API Name</th>
                    <th>Arguments</th>
                    <th>Return Code</th>
                </tr>
            </thead>
            <tfoot>
                <tr>
                
                </tr>
            </tfoot>

            <tbody>
                <template v-for="(inst_procs, inst_uuid) in proc_syscall_map">
                    <template v-for="(proc_syscalls, process_uuid) in inst_procs">
                    <tr v-if="proc_syscall_map[inst_uuid][process_uuid].length == 0">
                        <td v-if="process_uuid != '*'">
                            {{ process_map[process_uuid].path }}
                        </td>
                        <td v-else>
                            ALL processes
                        </td>
                        <td colspan="4" class="has-text-centered"><strong>No syscalls</strong></td>
                    </tr>
                    <tr v-for="syscall in proc_syscall_map[inst_uuid][process_uuid]">
                        <template v-if="syscall == '*'">
                            <td v-if="process_uuid != '*'">
                                {{ process_map[process_uuid].path }}
                            </td>
                            <td v-else>
                                ALL processes
                            </td>
                            <td colspan="4" class="has-text-centered"><strong>ALL syscalls</strong></td>
                        </template>
                        <template v-else>
                            <td>
                                {{ syscall.process.path }}
                            </td>
                            <td>
                                {{ syscall.name }}
                            </td>
                            <td class="allow-newlines m-0 limit-data">
                                <ul class="m-0 no-long">
                                    <li v-for="arg in syscall.args">{{ arg }}</li>
                                </ul>
                            </td>
                            <td class="allow-newlines limit-data" >
                                {{ syscall.return_code }}
                            </td>
                        </template>
                        
                    </tr>
                    </template>
                
                </template>
                
            </tbody>
        </table>
    </div>

    
    
</template>

<style scoped>

</style>

<script>
import time from "@/lib/time";
import api from "@/lib/api";
import helpers from "@/lib/helpers";

export default {
  data() {
    return {
        inserted: 'none',
        current_tab: 'events',
        checked_instances: [],
        add_processes_map: {},
        add_events_map: {},
        proc_event_map: {},
        proc_syscall_map: {},
        show_processes_map: {}, // For show/hiding the process lists
        show_events_map: {}, // For show/hiding the process lists
        exec_instance_data: {},
        process_map: {}
    }
  },
  emits: ["eventFilterUpdate"],
  props: {
    exec_instances: Array,
    toggle: Boolean,
    all_checked: Boolean,
    include_syscalls: Boolean,
    include_events: Boolean,
  },
  mounted() {
    var self = this;
    if (self.all_checked) {
        for (var i in self.exec_instances) {
            var instance_uuid = self.exec_instances[i].uuid;
            self.checked_instances.push(instance_uuid);
            if (self.include_events) {
                self.proc_event_map[instance_uuid] = {};
            }
            if (self.include_syscalls) {
                self.proc_syscall_map[instance_uuid] = {};
            }
        }
        
        self._sendFilterUpdate();
        
    }
  },
  computed: {
    getEventCount() {
        var proc_count = 0;
        var event_count = 0;
        var has_all_events = false;

        for (var inst in this.proc_event_map) {
            if (helpers.has_key(this.proc_event_map[inst], "*")) {
                if (this.proc_event_map[inst]['*'].length == 1) {
                    return "*:*"
                } else {
                    return "*:0"
                }
                
            } 
            for (var proc in this.proc_event_map[inst]) {
                proc_count += 1;
                if (this.proc_event_map[inst][proc].length == 1 && this.proc_event_map[inst][proc][0] == "*") {
                    has_all_events = true;
                } else {
                    event_count += this.proc_event_map[inst][proc].length;
                }
            }
        }
        if(has_all_events) {
            if (event_count > 0) {
                return proc_count + ":*+" + event_count;
            } else {
                return proc_count + ":*";
            }
            
        } else {
            return proc_count + ":" + event_count;
        }
    },
    getSyscallCount() {

    }
  },    
  methods: {
    _addToProcessMap(inst_uuid, process) {
        var self = this;

        process['inst_uuid'] = inst_uuid;
        self.process_map[process.uuid] = process;
        if (process['child_processes'].length > 0) {
            for (var i in process['child_processes']) {
                self._addToProcessMap(inst_uuid, process['child_processes'][i]);
            }
        }
    },
    _getGetExecInstData(inst_uuid) {
        var self = this;

        api.get_instance_data(inst_uuid,
            function(data) {
                self.exec_instance_data[inst_uuid] = data;

                console.log(self.exec_instance_data[inst_uuid]);

                for (var i in self.exec_instance_data[inst_uuid].processes) {
                    self._addToProcessMap(inst_uuid, self.exec_instance_data[inst_uuid].processes[i]);
                }
            },
            function(status, data) {

            }
        )
    },
    _mapToFilter(convert_map) {
        var filter = JSON.parse(JSON.stringify(convert_map));
        for (var inst_uuid in filter) {
            for (var proc_uuid in filter[inst_uuid]) {
                var old_array = filter[inst_uuid][proc_uuid];
                var new_array = [];

                for (var i in old_array) {
                    if (old_array[i] == "*") {
                        new_array.push(old_array[i]);

                    } else if (helpers.has_key(old_array[i], 'uuid')){
                        new_array.push(old_array[i].uuid);
                    } else if (helpers.has_key(old_array[i], '_id')){
                        new_array.push(old_array[i]._id);
                    }
                }
                filter[inst_uuid][proc_uuid] = new_array;
            }
        }
        return filter;
    },

    _sendFilterUpdate() {
        var filter = {
            events: this._mapToFilter(this.proc_event_map),
            syscalls: this._mapToFilter(this.proc_syscall_map)
        }
        
        this.$emit('eventFilterUpdate', filter);
    },
    instanceCheckClicked(uuid, value) {
        var self = this;
        if (value == true) {
            self.checked_instances.push(uuid);
        } else {
            const index = self.checked_instances.indexOf(uuid);
            if (index > -1) {
                self.checked_instances.splice(index, 1); 
            }
        }

        self._sendCheckedUpdate();
    },
    onProcessChecked(process, value) {
        var self = this;
        console.log(process, value)

        var inst_uuid = process['inst_uuid'];

        if (value == true) {
            helpers.ensure_key(self.proc_event_map, inst_uuid, {});
            helpers.ensure_key(self.proc_event_map[inst_uuid], process.uuid, []);

            
        } else {
            if (helpers.has_key(self.proc_event_map[inst_uuid][process.uuid])) {
                delete self.proc_event_map[inst_uuid][process.uuid];
            }
        }

        self._sendFilterUpdate();
    },
    onIncludeProcessSelect(exec_inst, value) {
        /*
        No self.proc_event_map[exec_uuid]       ==> Do not include exec_uuid
        self.proc_event_map[exec_uuid] = {}     ==> Include exec inst, with no processes
        self.proc_event_map[exec_uuid] = {     
            "*": []
        }                                       ==> Include exec inst, with all process, no events
        self.proc_event_map[exec_uuid] = {     
            proc_uuid: []
        }                                       ==> Include exec inst, with 'proc_uuid' process, no events
        self.proc_event_map[exec_uuid] = {     
            proc_uuid: ["*"]
        }                                       ==> Include exec inst, with 'proc_uuid' process, with all events
        self.proc_event_map[exec_uuid] = {     
            proc_uuid: [event_uuid]
        }                                       ==> Include exec inst, with 'proc_uuid' process, with 'event_uuid' event
        */
        var self = this;

        var inst_uuid = exec_inst.uuid;

        helpers.ensure_key(self.show_processes_map, inst_uuid, false);
        helpers.ensure_key(self.proc_event_map, inst_uuid, {});
        helpers.ensure_key(self.proc_syscall_map, inst_uuid, {});

        self.inserted = value;

        if (value == 'some') {
            self.show_processes_map[inst_uuid] = true;

            if (helpers.has_key(self.proc_event_map[inst_uuid], "*")) {
                delete self.proc_event_map[inst_uuid]["*"];
            }

            if (helpers.has_key(self.proc_syscall_map[inst_uuid], "*")) {
                delete self.proc_syscall_map[inst_uuid]["*"];
            }

            self.proc_event_map[inst_uuid] = {};
            self.proc_syscall_map[inst_uuid] = {};

            self._getGetExecInstData(inst_uuid);
        } else {
            self.show_processes_map[inst_uuid] = false;
            self.proc_event_map[inst_uuid] = {};

            if (value == 'all') {
                self.proc_event_map[inst_uuid]["*"] = ["*"];
                self.proc_syscall_map[inst_uuid]["*"] = ["*"];
            } else if (value == 'all_nodata') {
                self.proc_event_map[inst_uuid]["*"] = [];
                self.proc_syscall_map[inst_uuid]["*"] = [];
            } else if (value == 'all_noevents') {
                self.proc_event_map[inst_uuid]["*"] = [];
                self.proc_syscall_map[inst_uuid]["*"] = ["*"];
            } else if (value == 'all_nosyscalls') {
                self.proc_event_map[inst_uuid]["*"] = ["*"];
                self.proc_syscall_map[inst_uuid]["*"] = [];
            } else {
                if (helpers.has_key(self.proc_event_map, inst_uuid)) {
                    delete self.proc_event_map[inst_uuid];
                }
                if (helpers.has_key(self.proc_syscall_map, inst_uuid)) {
                    delete self.proc_syscall_map[inst_uuid];
                }
            } 
        }
        self._sendFilterUpdate();
    },
    // For selecting what is filtered for selected processes
    onProcessSelect(process, event_option, syscall_option) {
        var self = this;

        var inst_uuid = process['inst_uuid'];

        helpers.ensure_key(self.proc_event_map, inst_uuid, {});
        helpers.ensure_key(self.proc_event_map[inst_uuid], process.uuid, []);

        if (event_option == 'some') {
            self.proc_event_map[inst_uuid][process.uuid] = [];
        } else if (event_option == 'all') {
            self.proc_event_map[inst_uuid][process.uuid] = ["*"];
        } else if (event_option == 'none') {
            self.proc_event_map[inst_uuid][process.uuid] = [];
        }
        if (syscall_option == 'some') {
            self.proc_syscall_map[inst_uuid][process.uuid] = [];
        } else if (syscall_option == 'all') {
            self.proc_syscall_map[inst_uuid][process.uuid] = ["*"];
        } else if (syscall_option == 'none') {
            self.proc_syscall_map[inst_uuid][process.uuid] = [];
        }
        self._sendFilterUpdate();
    },
    onEventChecked(process, event_list) {
        var self = this;

        var inst_uuid = process['inst_uuid'];
        
        self.proc_event_map[inst_uuid][process.uuid] = event_list;
        self._sendFilterUpdate();
    },
    onSyscallChecked(process, syscall_list) {
        var self = this;

        var inst_uuid = process['inst_uuid'];
        
        self.proc_syscall_map[inst_uuid][process.uuid] = syscall_list;
        self._sendFilterUpdate();
    },
    toggleProcessList(inst_uuid) {
        this.show_processes_map[inst_uuid] = !this.show_processes_map[inst_uuid];
    },
    setProcessTab(new_tab) {
        this.current_tab = new_tab;
    }
  }
}
</script>