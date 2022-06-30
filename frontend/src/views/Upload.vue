<script setup>
import FileUploadList from '@/components/FileUploadList.vue'
import JobWait from '@/components/JobWait.vue'
</script>

<template>
    <div class="container">
        <FileUploadList @uploadfiles="submitFiles" v-if="stage == 'add'" ref="uploadListItem"></FileUploadList>
        <JobWait v-if="stage == 'wait'" ref="waitItem" :job_uuid="job_uuid"></JobWait>
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
        "job_uuid": ""
    }
  },
  mounted() {
    
  },
  methods: {
    submitFiles(file_list) {

        let formData = new FormData();
        for (var i in file_list) {
            formData.append('submissions[]', file_list[i]);
        }

        var self = this;

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
                self.stage = "wait";
                // console.log(job_uuid);
                // console.log(self.$refs);
                // self.stage = "wait";
                // self.$refs.waitItem.startWait(job_uuid);
                
            }
            // this.$refs.waitItem.startWait();

        })
        .catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>