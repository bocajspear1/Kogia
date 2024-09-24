<script setup>
import FileInfoBlock from '@/components/file/FileInfoBlock.vue';
import Progress from '@/components/general/Progress.vue';
import HexView from '@/components/general/HexView.vue';
import MenuButton from '@/components/menu/MenuButton.vue';
import MenuBar from '@/components/menu/MenuBar.vue';
import SubmissionList from '@/components/submission/SubmissionList.vue';
import MetadataTable from '@/components/metadata/MetadataTable.vue';

import TabMenuItem from '@/components/menu/TabMenuItem.vue';
import TabMenu from '@/components/menu/TabMenu.vue';
</script>

<template>

<div class="container column is-10" ref="my_column">
    <template  v-if="file != null && done == true">
         <FileInfoBlock :file="file"></FileInfoBlock>
         <MenuBar>
          <template v-slot:main>
            <MenuButton iconname="download" @click="download" tooltip="Raw download"></MenuButton>
            <MenuButton iconname="folder-zip" @click="zip_download" tooltip="Zipped download"></MenuButton>
            <MenuButton iconname="folder-key" @click="encrypt_download" tooltip="Encrypted download"></MenuButton>
            
            
          </template>
          <template v-slot:right>
            
          </template>
        </MenuBar>
        <div class="mt-2">
          <TabMenu>
            <template v-slot:main>
            <TabMenuItem iconname="view-list-outline" @click="setTab('submissions')" :active="tab=='submissions'">Submissions</TabMenuItem>
            <TabMenuItem iconname="table-multiple" @click="setTab('metadata')" :active="tab=='metadata'">Metadata</TabMenuItem>
            <TabMenuItem iconname="hexadecimal" @click="setTab('hexview')" :active="tab=='hexview'">View Hex</TabMenuItem>
            </template>
          </TabMenu>
        </div>
        
    </template>

   
    <Progress v-if="file != null && done != true"></Progress>
    <div v-if="file == null && done == true" class="notification is-warning">
        File not found
    </div>
    <template v-if="data_done && (tab == 'submissions')">
      <SubmissionList :submissions="submissions"></SubmissionList>
    </template>
    <template v-if="data_done && (tab == 'metadata')">
      <MetadataTable :file_uuid="getFileUUID()"></MetadataTable>
    </template>
    <template v-if="data_done && (tab == 'hexview')">
      <HexView :hexdata="hexdata" :width="hexdata_width"></HexView>
    </template>
    <iframe ref="download_iframe" style="display:none;"></iframe>
</div>
    
</template>

<style scoped>

</style>

<script>
import time from "@/lib/time";
import api from '@/lib/api';

export default {
  data() {
    return {
      file: null,
      done: false,
      data_done: false,
      tab: "",
      submissions: [],
      hexdata: "",
      hexdata_width: 32
    }
  },
  mounted() {
    this.getFile();
    this.setTab("submissions");
  },
  methods: {
    fileClicked(uuid, data) {
      console.log(uuid, data);
    },
    getFileUUID() {
        if (this.file == null) {
            return null;
        } else {
            return this.file['uuid'];
        }
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
    getFileHex() {
        var self = this;
        var file_uuid = self.$route.params.file_uuid;

        var column_count = self.$refs.my_column.clientWidth / 42;
        var set_columns = column_count - (column_count%16);
        if (set_columns == 0) {
          set_columns = 8;
        }
        api.get_file_hexdata(file_uuid,
            function(data) {
                self.hexdata_width = set_columns;
                self.hexdata = data;
            },
            function(status, data) {
                console.log('FAILURE!!', status, data);
            }
        );
    },
    download() {
      var self = this;
      api.get_file_token(self.$route.params.file_uuid,
            function(data) {
              var download_token = data['download_token'];
              self.$refs.download_iframe.src = '/api/v1/file/' + self.$route.params.file_uuid + "/download?format=raw&download_token=" + download_token;
            },
            function(status, data) {
                console.log('FAILURE!!', status, data);
            }
        );
    },
    zip_download() {
      var self = this;
      api.get_file_token(self.$route.params.file_uuid,
          function(data) {
            var download_token = data['download_token'];
            self.$refs.download_iframe.src = '/api/v1/file/' + self.$route.params.file_uuid + "/download?format=zip&download_token=" + download_token;
          },
          function(status, data) {
              console.log('FAILURE!!', status, data);
          }
      );
    },
    encrypt_download() {
      var self = this;
      api.get_file_token(self.$route.params.file_uuid,
            function(data) {
              var download_token = data['download_token'];
              self.$refs.download_iframe.src = '/api/v1/file/' + self.$route.params.file_uuid + "/download?format=enczip&download_token=" + download_token;
            },
            function(status, data) {
                console.log('FAILURE!!', status, data);
            }
        );
    },
    setTab(new_tab) {
      var self = this;
      self.tab = new_tab;
      if (new_tab == 'submissions') {
        self.submissions = [];
        var file_uuid = self.$route.params.file_uuid;
        self.data_done = false;
        api.get_submission_list(file_uuid,
            function(resp_data){
                for (var i in resp_data) {
                    var item = resp_data[i];
                    item['submit_time'] = time.seconds_to_string(item['submit_time']);
                    self.submissions.push(item);
                }
                self.data_done = true;
                console.log(self.submissions)
            },
            function(status, data){
                console.log('FAILURE!!', status, data);
            }
        )
      } else if (new_tab == 'hexview') {
        self.getFileHex()
      }
    }
  }
}
</script>