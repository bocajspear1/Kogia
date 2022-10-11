<script setup>
import FileInfoBlock from '@/components/FileInfoBlock.vue'
</script>

<template>

<div class="container column is-10">
    <FileInfoBlock v-if="file != null" :file="file"></FileInfoBlock>
</div>
    
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      file: null
    }
  },
  mounted() {
    this.getFile();
  },
  methods: {
    fileClicked(uuid, data) {
      console.log(uuid, data);
    },
    getFile() {
      var self = this;
      var file_uuid = self.$route.params.file_uuid;
      axios.get("/api/v1/file/" + file_uuid + "/info").then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                self.file = resp_data['result'];
                // var date = new Date(self.submission['submit_time']*1000);
                // self.submission['submit_time'] = date.toLocaleString() 
                self.done = true;
            }
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>