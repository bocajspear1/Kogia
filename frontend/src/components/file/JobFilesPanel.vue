<script setup>
import MenuBar from '@/components/menu/MenuBar.vue';
import MenuButton from '@/components/menu/MenuButton.vue';
import FileMultiSelectList from '@/components/file/FileMultiSelectList.vue';
</script>
<template>
    <MenuBar>
        <template v-slot:main>
            <MenuButton iconname="magnify-plus" @click="newSubmission" tooltip="Create new submission from selected" :disabled="selected_files.length == 0"></MenuButton>
                
        </template>
        <template v-slot:right>
            
        </template>
    </MenuBar>
    <FileMultiSelectList v-if="files != null" :toggle="false" :files="files" @file_clicked="fileClicked" @file_checked="fileChecked"></FileMultiSelectList>
    <div class="modal" ref="newsubmission">
        <div class="modal-background" @click="closeModal"></div>
        <div class="modal-content">
            <div class="box content">
                <div class="field">
                    <label class="label">Submission Name (required)</label>
                    <div class="control">
                        <input class="input" type="text" ref="nameInput">
                    </div>
                    <p class="help is-danger" v-if="error_message != ''">{{ error_message }}</p>
                </div>
                <div class="field">
                    <label class="label">Description (optional)</label>
                    <div class="control">
                        <textarea class="textarea" ref="descriptionInput"></textarea>
                    </div>
                </div>
                <ul>
                    <li v-for="file in selected_files">{{ file.name }}</li>
                </ul>
                <div class="message is-danger" v-if="submit_error != ''">
                    <div class="message-body">
                        Error while creating submission: {{ submit_error }}
                    </div>
                </div>
                <button class="button is-primary" @click="createSubmission">Create Submission</button>
            </div>
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
       selected_files: [],
       error_message: '',
       submit_error: ''
    }
  },
  props: ["files"],
  emits: [],
  mounted() {
    var self = this;

  },
  methods: {
    newSubmission() {
        var self = this;
        if (self.selected_files.length > 0) {
            self.$refs.newsubmission.classList.add('is-active');
        }
    },
    fileClicked(uuid, data) {
        this.$router.push({ name: 'FileSingle', params: { file_uuid: uuid } });
    },
    fileChecked(file_list) {
        this.selected_files = file_list;
    },
    closeModal() {
        var self = this;
        self.$refs.newsubmission.classList.remove('is-active');
    },
    createSubmission(){
        var self = this;
        self.error_message = "";
        
        let formData = new FormData();
        for (var i in self.selected_files) {
            console.log(self.selected_files[i])
            formData.append('file_uuids[]', self.selected_files[i].uuid);
        }

        var name = self.$refs.nameInput.value;
        formData.append('name', name);
        var description = self.$refs.descriptionInput.value;
        formData.append('description', description);

        if (name != "") {
            console.log("new submission", self.selected_files);
            api.api_post_form('/submission/new', formData, function(response){
                var resp_data = response;

                var submission_uuid = resp_data['submission_uuid'];
                self.$router.push({ name: 'JobCreate', params: { submission_uuid: submission_uuid } });
                self.closeModal();
            }, function(status, message){
                //self.$refs.notifications.addNotification("error", "Upload Error: " + resp);
                self.submit_error = message;
            })
            
        } else {
            self.error_message = "Submission name must be set";
        }
    }
  }
}
</script>
