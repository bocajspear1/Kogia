<script setup>
import DynamicFilterTable from '@/components/dynamic/DynamicFilterTable.vue'
</script>

<template>
<div class="container p-4">
    <div v-if="error != null" class="notification is-warning">
        {{ error }}
    </div>
    <div v-else-if="!types_done && (file_uuid != null || process_uuid != null || instance_uuid != null )">
        <progress class="progress is-medium is-primary" max="100">50%</progress>
    </div>
    <template v-else-if="types_done && error == null && (file_uuid != null || instance_uuid != null || process_uuid != null)">
        <div class="select is-fullwidth" v-if="Object.keys(metadata_types).length > 0 && types_done" >
            <select ref="metadataSelect" @change="onSelect">
                <option selected value="">Select Metadata Type</option>
                <template v-for="(value, metadata_type) in metadata_types">    
                <option :value="metadata_type">{{ metadata_type }} ({{value}})</option>
                </template>
            </select>
        </div>
        <div class="notification is-warning" v-else-if="types_done">
            No metadata found
        </div>
        <DynamicFilterTable v-if="selected_type != ''" 
                    :columns="['Values']" 
                    :data="metadata_list" 
                    :pageSize="limit"
                    :totalItems="metadata_count"
                    :loading="list_loading"
                    @onFilter="onFilter" 
                    @onNewPage="onNewPage" :selectable="selectable" :select_column="0" @onItemSelect="onItemSelect"></DynamicFilterTable>

    </template>
    <div class="notification is-info" v-else-if="!list_loading">
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
        types_done: false,
        list_loading: false,
        limit: 50,
        error: null,
        metadata_types: {},
        metadata_count: 0,
        metadata_list: [],
        selected_type: "",
        current_page: 1,
        filter: ""
    }
  },
  props: ["file_uuid", "process_uuid", "instance_uuid", "selectable"],
  emits: ["metadataSelected"],
  mounted() {
    this.getMetadataTypeList();
  },
  watch: {
    'file_uuid' (to, from) {
        this._reset();
        this.getMetadataTypeList();
    },
    'instance_uuid' (to, from) {
        this._reset();
        this.getMetadataTypeList();
    },
    'process_uuid' (to, from) {
        this._reset();
        this.getMetadataTypeList();
    }
  },
  methods: {
    _reset() {
        if (this.$refs.metadataSelect) {
            this.$refs.metadataSelect.selectedIndex = 0;
        }
        this.metadata_list = [];
        this.selected_type = "";
        this.current_page = 1;
    },
    _updateMetadataTypes(data) {
        var self = this;
        self.error = null;
        
        self.metadata_types = data;
        self.current_page = 1;
        self.metadata_count = 0;
        self.types_done = true;
    },
    _metadataError(status, data) {
        var self = this;
        self.error = data;
    },
    getMetadataTypeList() {
        var self = this;
        self.types_done = false;
        if (self.file_uuid != null) {
            api.get_file_metadata_types(self.file_uuid, self._updateMetadataTypes, self._metadataError);
        } else if (self.instance_uuid != null) {
            api.get_instance_metadata_types(self.instance_uuid, self._updateMetadataTypes, self._metadataError);
        } else if (self.process_uuid != null) {
            api.get_process_metadata_types(self.process_uuid, self._updateMetadataTypes, self._metadataError);
        } 
    },
    onSelect(event) {
        if (event.target.value != "") {
            this.selected_type = event.target.value;
            this.updateSelectFilter();
        }
    },
    _updateMetadataList(resp_data) {
        var self = this;
        self.error = null;
        
        self.metadata_count = resp_data['total'];

        for (var i = 0; i < resp_data['metadata'].length; i++) {
            self.metadata_list.push([resp_data['metadata'][i]['value']])
        }
        self.list_loading = false;
    },
    updateSelectFilter() {
        var self = this;
        self.list_loading = true;
        self.metadata_list = [];
        
        if (self.file_uuid != null) {
            api.get_file_metadata_list(self.file_uuid, self.selected_type, self.filter, (self.current_page-1)*self.limit, self.limit, self._updateMetadataList, self._metadataError);
        } else if (self.instance_uuid != null) {
            api.get_instance_metadata_list(self.instance_uuid, self.selected_type, self.filter, (self.current_page-1)*self.limit, self.limit, self._updateMetadataList, self._metadataError);
        } else if (self.process_uuid != null) {
            api.get_process_metadata_list(self.process_uuid, self.selected_type, self.filter, (self.current_page-1)*self.limit, self.limit, self._updateMetadataList, self._metadataError);
        }
    },
    onFilter: function(column, new_filter) {
        this.filter = new_filter;
        this.updateSelectFilter();
        this.current_page = 1;
    },
    onNewPage(new_page) {
        if (this.current_page != new_page) {
            console.log("updated page to ", new_page)
            this.current_page = new_page;
            this.updateSelectFilter();
            
        }
    },
    onItemSelect(row_item, value) {
        if (!this.selectable) {
            return;
        }
        this.$emit("metadataSelected", this.selected_type, row_item, value);
    }
  }
}
</script>