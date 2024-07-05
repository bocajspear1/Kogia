<script setup>
import EventTable from '@/components/host/EventTable.vue'
import SyscallTable from '@/components/host/SyscallTable.vue'
import ProcessNodes from '@/components/host/ProcessNodes.vue'
import TabMenuItem from '@/components/menu/TabMenuItem.vue';
import TabMenu from '@/components/menu/TabMenu.vue';
</script>
<template>
    <div class="card m-2">
        <header class="card-header">
            <span class="card-header-title">{{ process.path }} ({{ process.pid }})</span>
        </header>
        <div class="card-content">
            <div class="content">
                <TabMenu>
                    <template v-slot:main>
                    <TabMenuItem iconname="clock" @click="setProcessTab('events')" :active="current_tab=='events'">Events</TabMenuItem>
                    <TabMenuItem iconname="card-search" @click="setProcessTab('syscalls')" :active="current_tab=='syscalls'">Syscalls</TabMenuItem>
                    </template>
                </TabMenu>
                <div class="m-5 p-2" v-show="current_tab == 'events'">
                    <div class="field is-grouped">
                        <p class="control">
                            <div class="select">
                                <select @change="onEventSelect($event.target.value)">
                                    <option selected value="none">Include NO events</option>
                                    <option value="all">Include ALL events</option>
                                    <option value="some">Include SOME events</option>
                                </select>
                            </div>
                        </p>
                        <p class="control">
                            <button class="button is-link" @click="toggleEventList" v-if="event_select_option =='some'">
                                <span v-if="show_events">Hide event list</span>
                                <span v-if="!show_events">Show event list</span>
                            </button>
                        </p>
                    </div>
                    <div>
                        <EventTable v-show="show_events" :selectable="true" :process_uuid="process.uuid" @event_checked="onEventChecked"></EventTable>
                    </div>
                    
                </div>
                <div class="m-5 p-2" v-show="current_tab == 'syscalls'">
                    <div class="field is-grouped">
                        <p class="control">
                            <div class="select">
                                <select @change="onSyscallSelect($event.target.value)">
                                    <option selected value="none">Include NO syscalls</option>
                                    <option value="all">Include ALL syscalls</option>
                                    <option value="some">Include SOME syscalls</option>
                                </select>
                            </div>
                        </p>
                        <p class="control">
                            <button class="button is-link" @click="toggleSyscallList" v-if="syscall_select_option =='some'">
                                <span v-if="show_syscalls">Hide syscall list</span>
                                <span v-if="!show_syscalls">Show syscall list</span>
                            </button>
                        </p>
                    </div>
                    <div>
                        <SyscallTable v-show="show_syscalls" :selectable="true" :process_uuid="process.uuid" @syscallChecked="onSyscallChecked"></SyscallTable>
                    </div>
                </div>
                
            </div>
        </div>     
    </div>
</template>

<style scoped>

</style>

<script>
export default {
  data() {
    return {
        current_tab: "events",
        show_events: false,
        show_syscalls: false,
        event_select_option: "none",
        syscall_select_option: "none",
        selected_events: [],
        selected_syscalls: []
    }
  },
  emits: ["selectUpdated", "eventChecked", "syscallChecked"],
  props: {
    process: Object,
  },
  mounted() {
    var self = this;
    
  },
  computed: {
    
  },    
  methods: {
    mounted() {
        self.$emit("selectUpdated", this.process, "none");
    },
    // When event dropdown on process is selected
    onEventSelect: function(value) {
        var self = this;
        self.event_select_option = value;
        self.$emit("selectUpdated", self.process, self.event_select_option, self.syscall_select_option);
        if (value == 'some') {
            self.show_events = true;
        } else {
            self.show_events = false;
        }
    },
    onSyscallSelect: function(value) {
        var self = this;
        self.syscall_select_option = value;
        self.$emit("selectUpdated", self.process, self.event_select_option, self.syscall_select_option);
        if (value == 'some') {
            self.show_syscalls = true;
        } else {
            self.show_syscalls = false;
        }
    },
    onEventChecked(event, value) {
        var self = this;

        event['process'] = self.process;

        if (value == true) {
            self.selected_events.push(event)
        } else {
            for (var i in self.selected_events) {
                if (self.selected_events[i].uuid == event.uuid) {
                    self.selected_events.splice(i, 1); 
                }
            }
        }
        self.$emit("eventChecked", self.process, self.selected_events);
    },
    onSyscallChecked(syscall, value) {
        var self = this;

        syscall['process'] = self.process;

        if (value == true) {
            self.selected_syscalls.push(syscall)
        } else {
            for (var i in self.selected_events) {
                if (self.selected_syscalls[i]._d == syscall._id) {
                    self.selected_syscalls.splice(i, 1); 
                }
            }
        }
        self.$emit("syscallChecked", self.process, self.selected_syscalls);
    },
    toggleEventList() {
        this.show_events = !this.show_events;
    },
    toggleSyscallList() {
        this.show_syscalls = !this.show_syscalls;
    },
    setProcessTab(new_tab) {
        this.current_tab = new_tab;
    }
  }
}
</script>