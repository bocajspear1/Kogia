<script setup>
import FileIcon from '@/components/file/FileIcon.vue'
</script>
<template>
    <div class="list has-hoverable-list-items has-visible-pointer-controls">
        <div v-for="file in files" class="list-item is-clickable" @click="clickFile(file.uuid)" :ref="file.uuid">
            <div class="list-item-image p-2">
                <FileIcon :file="file"></FileIcon>
            </div>
            <div class="list-item-content">
                <div class="list-item-title">{{ file.name }}</div>
                <div class="list-item-description">
                    <span class="tag m-1">
                        <strong>Architecture:</strong>&nbsp;{{ file.exec_arch }}
                    </span>
                    <span class="tag m-1">
                        <strong>Bits:</strong>&nbsp;{{ file.exec_bits }}
                    </span>
                    <span class="tag m-1">
                        <strong>OS:</strong>&nbsp;{{ file.target_os }}
                    </span>
                    <span class="tag m-1">
                        <strong>Format:</strong>&nbsp;{{ file.exec_format }}
                    </span>
                    <span class="tag m-1" v-if="file.exec_packer != ''">
                        <strong>Packer:</strong>&nbsp;{{ file.exec_packer }}
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
        current: null
    }
  },
  emits: ["file_clicked"],
  props: {
    files: Array,
    toggle: Boolean
  },
  mounted() {
    
  },
  methods: {
    clickFile(uuid) {
        var toggled = false;
        if (this.toggle) {
            
            if (this.current == uuid) {
                this.$refs[uuid][0].classList.remove('has-background-grey-light');
                this.current = null;
                toggled = false;
            } else {
                if (this.current != null) {
                    this.$refs[this.current][0].classList.remove('has-background-grey-light');
                }
                this.$refs[uuid][0].classList.add('has-background-grey-light')
                this.current = uuid;
                toggled = true;
            }
        }
        var file_data = null;
        for (var i in this.files) {
            if (this.files[i].uuid == uuid) {
                file_data = this.files[i]
            }
        }
        this.$emit('file_clicked', uuid, file_data, toggled);
    }
  }
}
</script>