<script setup>
import FileIcon from '@/components/file/FileIcon.vue'
import GenericDropdown from '@/components/generic/GenericDropdown.vue'
</script>
<template>

<GenericDropdown @item_selected="onSelect" colorClass="is-success" ref="intDropdown" :initSelect="selected">
    <template v-slot:selected="selected">
        <span v-if="selected.selected == null" >
            <mdicon name="help-circle-outline" :size="25" />
            &nbsp;&nbsp;Select a File
        </span>
        <span v-if="selected.selected != null">
            <FileIcon :file="selected.selected" :size="25" ></FileIcon>&nbsp;
            {{ selected.selected.name }}
        </span>
    </template>
    <template v-slot:dropcontent="dropcontent">
        <template v-if="files.length != 0">
        <a v-for="file in files" class="dropdown-item" @click="dropcontent.onSelect(file)">
            <FileIcon :file="file" :size="30" ></FileIcon>&nbsp;{{ file.name }}
                
            <span class="tag m-1">
                <strong>Type:</strong>&nbsp;{{ file.mime_type }}
            </span>
        </a>
        </template>
        <template v-if="files.length == 0">
            <span class="dropdown-item">No files</span>
        </template>
    </template>
</GenericDropdown>

</template>

<style scoped>

</style>

<script>

export default {
  data() {
    return {
        current_file: null,
        active: false,
    }
  },
  emits: ["file_selected"],
  props: {
    files: Array,
    selected: null
  },
  mounted() {
    if (this.selected) {
        this.current_file = this.selected;
    }
  },
  unmounted() {
    
  },
  methods: {
    onSelect(file) {
        this.current_file = file;
        this.$emit('file_selected', file);
    }
  }
}
</script>