<script setup>
import MetadataTable from '@/components/metadata/MetadataTable.vue';
import TabMenuItem from '@/components/menu/TabMenuItem.vue';
import TabMenu from '@/components/menu/TabMenu.vue';
import ExecInstDropdown from '@/components/host/ExecInstDropdown.vue';
import ProcessDropdown from '@/components/host/ProcessDropdown.vue';
import FileDropdown from '@/components/file/FileDropdown.vue';
</script>
<template>
    <TabMenu>
    <template v-slot:main>
        <TabMenuItem iconname="folder-file" @click="metadataTabSelected('files')" :active="metadata_selected=='files'">Files</TabMenuItem>
        <TabMenuItem iconname="application-braces" @click="metadataTabSelected('execinst')" :active="metadata_selected=='execinst'">Execution Instances</TabMenuItem>
        <TabMenuItem iconname="file-cog" @click="metadataTabSelected('processes')" :active="metadata_selected=='processes'">Processes</TabMenuItem>
    </template>
    </TabMenu>
    <template v-if="metadata_selected=='files'">
        <FileDropdown :files="files" @file_selected="fileSelected" :selected="selected_file_i"></FileDropdown>
        <MetadataTable :file_uuid="getFileUUID()" :selectable="selectable" @metadataSelected="onMetadataSelected"></MetadataTable>
    </template>
    <template v-if="metadata_selected=='execinst'">
        <ExecInstDropdown :job_uuid="job.uuid" @execinst_selected="instanceSelected" :selected="selected_instance_i"></ExecInstDropdown>
        <MetadataTable v-if="selected_instance_i != null" :instance_uuid="getInstanceUUID()" 
            :selectable="selectable"
            @metadataSelected="onMetadataSelected"></MetadataTable>
    </template>
    <template v-if="metadata_selected=='processes'">
        <ExecInstDropdown :job_uuid="job.uuid" @execinst_selected="instanceSelected" :selected="selected_instance_i"></ExecInstDropdown>
        <span v-if="selected_instance_i != null" class="m-2 is-vcentered" >
            <ProcessDropdown ref="procDropdown" :processes="selected_instance_i.processes" @process_selected="processSelected"></ProcessDropdown>
        </span>
        <MetadataTable v-if="selected_process_i != null" 
            :process_uuid="getProcessUUID()" 
            :selectable="selectable"
            @metadataSelected="onMetadataSelected"></MetadataTable>
    </template>
    
</template>

<style scoped>

</style>

<script>
import time from "@/lib/time";
import api from "@/lib/api";

export default {
    data() {
        return {
            metadata_selected: 'files',
            files: [],
            selected_file_i: null,
            selected_instance_i: null,
            selected_process_i: null,
        }
    },
    emits: ["metadataSelected"],
    props: {
        job: Object,
        selectable: Boolean,
        selected_instance: Object,
        selected_file: Object
    },
    mounted() {
        this.selected_instance_i = this.selected_instance;
        this.selected_file_i = this.selected_file;
        this.getSubmission(this.job.submission);
    },
    methods: {
        // Get data data about submission, particularly files
        getSubmission(submission_uuid) {
            var self = this;
            
            api.get_submission_info(submission_uuid, function(result) {
                self.files = result.files;
            }, function(status, error){
                console.log('FAILURE!!', status, error);
            });
        },
        getFileUUID() {
            if (this.selected_file_i == null) {
                return null;
            } else {
                return this.selected_file_i['uuid'];
            }
        },  
        getInstanceUUID() {
            if (this.selected_instance_i == null) {
                return null;
            } else {
                return this.selected_instance_i['uuid'];
            }
        },  
        getProcessUUID() {
            if (this.selected_process_i == null) {
                return null;
            } else {
                return this.selected_process_i['uuid'];
            }
        },  
        metadataTabSelected(metadata_type) {
            this.metadata_selected = metadata_type;
            if (metadata_type == "processes") {
                this.selected_process_i = null;
            }
        },
        fileSelected(file) {
            this.selected_file_i = file;
        },
        instanceSelected(instance) {
            var self = this;
            self.selected_process_i = null;

            api.get_instance_data(instance.uuid,
                function(data) {
                    data = time.add_pretty_times(data, ['start_time', 'end_time'], [['start_time', 'end_time', 'duration']]);
                    self.selected_instance_i = data;
                    
                },
                function(status, data) {

                }
            )
        },
        processSelected(process) {
            this.selected_process_i = process;
        },
        // When metadata is checked in MetadataTable
        onMetadataSelected(metadata_type, key, value) {
            this.$emit("metadataSelected", metadata_type, key, value);
        }
    }
}
</script>