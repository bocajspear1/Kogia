<script setup>
import DynamicFilterTable from '@/components/dynamic/DynamicFilterTable.vue'
</script>

<template>
<div class="container p-4">
    <div v-if="error != null" class="notification is-warning">
        {{ error }}
    </div>
    <template v-else-if="error == null && (file_uuid != null || instance_uuid != null || process_uuid != null)">
        <div class="select is-fullwidth">
            <select ref="metadataSelect">
                <option selected>Select Metadata Type</option>
                <template v-for="(value, metadata_type) in metadata_types">    
                <option @click="onSelect(metadata_type)">{{ metadata_type }} ({{value}})</option>
                </template>
            </select>
        </div>
        <DynamicFilterTable v-if="selected_type != ''" :columns="['Values']" :data="metadata_list" :pageCount="2" @onFilter="onFilter"></DynamicFilterTable>
    </template>
    <div class="notification is-info" v-else>
        No item is selected
    </div>
</div>
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";

export default {
  data() {
    return {
        done: false,
        error: null,
        metadata_types: [],
        metadata_list: [],
        selected_type: ""
    }
  },
  props: ["file_uuid", "process_uuid", "instance_uuid"],
  mounted() {
    this.getMetadataList();
  },
  watch: {
    'file_uuid' (to, from) {
        this._reset();
        this.getMetadataList();
    },
    'instance_uuid' (to, from) {
        this._reset();
        this.getMetadataList();
    },
    'process_uuid' (to, from) {
        this._reset();
        this.getMetadataList();
    }
  },
  methods: {
    _reset() {
        if (this.$refs.metadataSelect) {
            this.$refs.metadataSelect.selectedIndex = 0;
        }
        this.metadata_list = [];
        this.selected_type = "";
    },
    _updateMetadataTypes(data) {
        var self = this;
        self.error = null;
        self.metadata_types = data;
    },
    _metadataError(status, data) {
        var self = this;
        self.error = data;
    },
    getMetadataList() {
        var self = this;
        console.log(self)

        if (self.file_uuid != null) {
            api.get_file_metadata_types(self.file_uuid, self._updateMetadataTypes, self._metadataError);
        } else if (self.instance_uuid != null) {
            api.get_instance_metadata_types(self.instance_uuid, self._updateMetadataTypes, self._metadataError);
        } else if (self.process_uuid != null) {
            api.get_process_metadata_types(self.process_uuid, self._updateMetadataTypes, self._metadataError);
        } 
    },
    onSelect(metadata_type) {
        console.log("onSelect")
        this.selected_type = metadata_type;
        this.updateSelectFilter("");
    },
    _updateMetadataList(data) {
        var self = this;
        self.error = null;
        self.metadata_list = [];
        for (var i = 0; i < data.length; i++) {
            self.metadata_list.push([data[i]])
        }
    },
    updateSelectFilter(filter) {
        var self = this;
        console.log("update select filter")
        if (self.file_uuid != null) {
            api.get_file_metadata_list(self.file_uuid, self.selected_type, filter, self._updateMetadataList, self._metadataError);
        } else if (self.instance_uuid != null) {
            api.get_instance_metadata_list(self.instance_uuid, self.selected_type, filter, self._updateMetadataList, self._metadataError);
        } else if (self.process_uuid != null) {
            api.get_process_metadata_list(self.process_uuid, self.selected_type, filter, self._updateMetadataList, self._metadataError);
        }
    },
    onFilter: function(column, new_filter) {
        this.updateSelectFilter(new_filter)
    }
  }
}
</script>