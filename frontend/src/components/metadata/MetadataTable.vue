<script setup>
import DynamicFilterTable from '@/components/dynamic/DynamicFilterTable.vue'
</script>

<template>
<div class="container p-4">
    <div v-if="error != null" class="notification is-warning">
        {{ error }}
    </div>
    <template v-else-if="error == null && file_uuid != null">
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
        Select a file to view metadata
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
  props: ["file_uuid"],
  mounted() {
    this.getMetadataList();
  },
  watch: {
    'file_uuid' (to, from) {
        if (this.$refs.metadataSelect) {
            this.$refs.metadataSelect.selectedIndex = 0;
        }
        
        this.getMetadataList();
        this.metadata_list = [];
        this.selected_type = "";
    }
  },
  methods: {
    getMetadataList() {
        var self = this;

        if (self.file_uuid != null) {
            api.get_file_metadata_types(self.file_uuid, 
                function(data){
                    self.error = null;
                    self.metadata_types = data;
                },
                function(status, data){
                    self.error = data;
                }
            )
        }
    },
    onSelect(metadata_type) {
        this.selected_type = metadata_type;
        this.updateSelectFilter("");
    },
    updateSelectFilter(filter) {
        var self = this;
        if (self.file_uuid != null) {
            if (self.selected_type == "") {
                self.selected_type = " ";
            }
            api.get_file_metadata_list(self.file_uuid, self.selected_type, filter,
                function(data){
                    self.error = null;
                    self.metadata_list = [];
                    for (var i = 0; i < data.length; i++) {
                        self.metadata_list.push([data[i]])
                    }
                    
                },
                function(status, data){
                    self.error = data;
                }
            )
        }
    },
    onFilter: function(column, new_filter) {
        this.updateSelectFilter(new_filter)
    }
  }
}
</script>