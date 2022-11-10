<script setup>
import FileInfoBlock from '@/components/file/FileInfoBlock.vue';
import Progress from '@/components/general/Progress.vue';
import MenuButton from '@/components/menu/MenuButton.vue';
import MenuBar from '@/components/menu/MenuBar.vue';
</script>

<template>

<div class="container column is-10">
    <template  v-if="file != null && done == true">
         <FileInfoBlock :file="file"></FileInfoBlock>
         <MenuBar>
          <template v-slot:main>
            <MenuButton iconname="download" @click="download"></MenuButton>
            
            
          </template>
          <template v-slot:right>
            
          </template>
        </MenuBar>
        <div class="tabs">
            <ul>
                <li class="is-active"><a>Jobs</a></li>
                <li><a>Submissions</a></li>
                <li><a>Metadata</a></li>
                <li><a>Tools</a></li>
            </ul>
        </div>
    </template>

   
    <Progress v-if="file != null && done != true"></Progress>
    <div v-if="file == null && done == true" class="notification is-warning">
        File not found
    </div>
</div>
    
</template>

<style scoped>

</style>

<script>
import axios from 'axios';
import api from '@/lib/api';

export default {
  data() {
    return {
      file: null,
      done: false,
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
        api.get_file_info(file_uuid,
            function(data) {
                self.file = data;
                self.done = true;
            },
            function(status, data) {
                self.done = true;
                console.log('FAILURE!!', status, data);
            }
        );
    },
    download() {

    }
  }
}
</script>