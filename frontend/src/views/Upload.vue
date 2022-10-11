<script setup>
import FileUploadList from '@/components/FileUploadList.vue'
import JobWait from '@/components/JobWait.vue'
import Notifications from '@/components/Notifications.vue'
</script>

<template>
    <div class="container column is-10">
        <Notifications ref="notifications"></Notifications>
        
        <div id="add-details" v-if="stage == 'add'" class="box">
            <div class="field">
                <label class="label">Submission Name (required)</label>
                <div class="control">
                    <input class="input" type="text" ref="nameInput">
                </div>
            </div>
            <div class="field">
                <label class="label">Description (optional)</label>
                <div class="control">
                    <textarea class="textarea" ref="descriptionInput"></textarea>
                </div>
            </div>
            <FileUploadList v-if="stage == 'add'" @uploadfiles="submitFiles" ref="uploadListItem"></FileUploadList>
        </div>
        
        <JobWait v-if="stage == 'wait'" ref="waitItem" :job_uuid="job_uuid" @jobdone="onJobDone" ></JobWait>
    </div>
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
        "stage": "add",
        "job_uuid": "",
        "submission_uuid": ""
    }
  },
  mounted() {
    
  },
  methods: {
    onJobDone(job_data) {
        this.$router.push({ name: 'JobCreate', params: { submission_uuid: this.submission_uuid } });
    },
    submitFiles(file_list) {

        let formData = new FormData();
        for (var i in file_list) {
            formData.append('submissions[]', file_list[i]);
        }

        var self = this;

        var name = self.$refs.nameInput.value;
        formData.append('name', name);
        var description = self.$refs.descriptionInput.value;
        formData.append('description', description);

        axios.post('api/v1/submission/new',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }
        ).then(function(resp){
            console.log('SUCCESS!!', resp);
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                var job_uuid = resp_data['result']['job_uuid'];
                self.job_uuid = job_uuid;
                self.submission_uuid = resp_data['result']['submission_uuid'];
                self.stage = "wait";
             
            } else {
                self.$refs.notifications.addNotification("error", "Upload Error: " + resp_data['error']);
            }
        })
        .catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>