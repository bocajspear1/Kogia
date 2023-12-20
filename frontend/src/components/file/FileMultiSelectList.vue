<script setup>
import FileIcon from '@/components/file/FileIcon.vue'
</script>
<template>
    <div class="list">
        <div v-for="file in files" class="list-item" :ref="file.uuid">
            <div class="list-item-image p-2">
                <label class="checkbox m-4">
                    <input type="checkbox" @input="checkClicked(file.uuid, $event.target.checked)" >
                </label>
                
                <FileIcon :file="file"></FileIcon>
            </div>
            <div class="list-item-content">
                <div class="list-item-title">
                    <span title="This file was dropped by an execution instance">
                        <mdicon name="folder-arrow-down" :size="20" v-if="file.dropped" class="m-1"/>
                    </span>
                    <a @click="clickFile(file.uuid)">{{ file.name }}</a>
                </div>
                <div class="list-item-description">
                    <span class="tag m-1" v-if="file.exec_arch != ''">
                        <strong>Architecture:</strong>&nbsp;{{ file.exec_arch }}
                    </span>
                    <span class="tag m-1" v-if="file.exec_bits != ''">
                        <strong>Bits:</strong>&nbsp;{{ file.exec_bits }}
                    </span>
                    <span class="tag m-1" v-if="file.target_os != ''">
                        <strong>OS:</strong>&nbsp;{{ file.target_os }}
                    </span>
                    <span class="tag m-1" v-if="file.exec_format != ''">
                        <strong>Format:</strong>&nbsp;{{ file.exec_format }}
                    </span>
                    <span class="tag m-1" v-if="file.exec_packer != ''">
                        <strong>Packer:</strong>&nbsp;{{ file.exec_packer }}
                    </span>
                    <span class="tag m-1" v-if="file.exec_arch == '' && file.target_os == ''">
                        <strong>MIME:</strong>&nbsp;{{ file.mime_type }}
                    </span>

                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>

</style>

<script>
export default {
  data() {
    return {
        current: null,
        checked_files: []
    }
  },
  emits: ["file_clicked", "file_checked"],
  props: {
    files: Array,
    toggle: Boolean,
  },
  mounted() {
    
  },
  methods: {
    _getFileData(file_uuid) {
        for (var i in this.files) {
            if (this.files[i].uuid == file_uuid) {
                return this.files[i]
            }
        }
    },
    clickFile(uuid) {
        var self = this;
        this.$emit('file_clicked', uuid, self._getFileData(uuid), false);
    },
    checkClicked(uuid, value) {
        var self = this;
        if (value == true) {
            self.checked_files.push(uuid);
        } else {
            const index = self.checked_files.indexOf(uuid);
            if (index > -1) {
                self.checked_files.splice(index, 1); 
            }
        }

        var out_list = [];
        for (var i = 0; i < self.checked_files.length; i++) {
            out_list.push(self._getFileData(self.checked_files[i]));
        }
        this.$emit('file_checked', out_list);
    }
  }
}
</script>