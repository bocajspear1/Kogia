<script setup>
import NetworkCommTable from "@/components/host/NetworkCommTable.vue";
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
                                <select @change="onIncludeNetCommSelect(exec_instance, $event.target.value)">
                                    <option selected value="all">Include NO network communications</option>
                                    <option value="none">Include ALL network communications</option>
                                    <option value="some">Include SOME network communications</option>
                                </select>
                            </div>
                        </p>
                        <p class="control">
                            <button class="button is-link" @click="toggleNetCommList(exec_instance.uuid)" v-if="select_map[exec_instance.uuid] != undefined && select_map[exec_instance.uuid] == 'some'">
                                <span v-if="show_map[exec_instance.uuid]">Hide communications list</span>
                                <span v-if="!show_map[exec_instance.uuid]">Show communications list</span>
                            </button>
                        </p>
                    </div>

                    <template v-if="select_map[exec_instance.uuid] != undefined && select_map[exec_instance.uuid] == 'some'">
                        <NetworkCommTable v-show="show_map[exec_instance.uuid]" :instance_uuid="exec_instance.uuid" :selectable="true" @netCommChecked="onNetCommChecked"></NetworkCommTable>
                    </template>

                </div>
            </div>
        </div>
    </div>

   
    
    
    
    <table class="table is-striped is-fullwidth m-5" v-if="Object.keys(netcomm_map).length > 0">
            <thead>
                <tr>
                    <th>Protocol</th>
                    <th>Source</th>
                    <th>Destination</th>
                    <th>Data</th>
                </tr>
            </thead>
            <tfoot>
                <tr>
                
                </tr>
            </tfoot>

            <tbody>
                <template v-for="(inst_netcomms, inst_uuid) in netcomm_map">
                    <tr v-for="netcomm in inst_netcomms">
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
                            <pre>{{ netcomm.data }}</pre>
                        </td>
                        
                    </tr>
                </template>

            </tbody>
        </table>
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";
import helpers from "@/lib/helpers";


export default {
  data() {
    return {
        current_instance: null,
        instance_count: null,
        netcomm_map: {},
        select_map: {},
        show_map: {}
    }
  },
  props: ["exec_instances", "all_checked"],
  emits: ["netCommFilterUpdate"],
  mounted() {
    var self = this;
    for (var i in self.exec_instances) {
        self.select_map[self.exec_instances[i].uuid] = true;
        self.show_map[self.exec_instances[i].uuid] = true;
        if (self.all_checked) {
            self.netcomm_map[self.exec_instances[i].uuid] = [];
        }
    }
    if (self.all_checked) {
        self._sendFilterUpdate();
    }
  },
  methods: {
    setTab(new_tab) {
        this.tab = new_tab;
    },
    _sendFilterUpdate() {
        var self = this;
        var filter = JSON.parse(JSON.stringify(self.netcomm_map));
        for (var inst_uuid in filter) {
            var old_array = filter[inst_uuid];
            var new_array = [];
            console.log(old_array)
            for (var i in old_array) {
                if (old_array[i] == "*") {
                    new_array.push(old_array[i]);

                } else if (helpers.has_key(old_array[i], 'uuid')){
                    new_array.push(old_array[i].uuid);
                } else if (helpers.has_key(old_array[i], '_id')){
                    new_array.push(old_array[i]._id);
                }
            }
            filter[inst_uuid] = new_array;
        }

        this.$emit("netCommFilterUpdate", filter);
    },
    instanceSelected(new_instance) {
        var self = this;
        
        api.get_instance_data(new_instance.uuid,
            function(data) {
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
    toggleNetCommList(instance_uuid) {
        this.show_map[instance_uuid] = !this.show_map[instance_uuid];
    },
    onIncludeNetCommSelect(exec_instance, value) {
        console.log(exec_instance, value)
        this.select_map[exec_instance.uuid] = value;
    },
    onNetCommChecked(netComm, value) {
        var self = this;

        var inst_uuid = netComm['instance_uuid'];

        helpers.ensure_key(self.netcomm_map, inst_uuid, [])

        if (value == true) {
            self.netcomm_map[inst_uuid].push(netComm)
        } else {
            for (var i in self.netcomm_map[inst_uuid]) {
                if (self.netcomm_map[inst_uuid][i].uuid == netComm.uuid) {
                    self.netcomm_map[inst_uuid].splice(i, 1); 
                }
            }
            if (self.netcomm_map[inst_uuid].length == 0) {
                delete self.netcomm_map[inst_uuid];
            }
        }

        self._sendFilterUpdate();
    }
  }
}
</script>
