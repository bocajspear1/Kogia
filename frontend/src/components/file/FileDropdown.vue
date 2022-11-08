<script setup>
import FileIcon from '@/components/file/FileIcon.vue'
</script>
<template>
<div class="dropdown" ref="dropdownClass">
    <div class="dropdown-trigger">
        <button class="button is-info is-light" aria-haspopup="true" aria-controls="dropdown-menu" @click="onClick">
        <span v-if="current_file == null" >
            <mdicon name="help-circle-outline" :size="25" />
            &nbsp;&nbsp;Select a File
        </span>
        <span v-if="current_file != null">
            <FileIcon :file="current_file" :size="25" ></FileIcon>
            {{ current_file.name }}
        </span>
        <span class="icon is-small">
            <mdicon name="chevron-down" :size="30" />
        </span>
        </button>
    </div>
    <div class="dropdown-menu" id="dropdown-menu" role="menu">
        <div class="dropdown-content">
            <template v-if="files.length != 0">
            <a v-for="file in files" class="dropdown-item" @click="onSelect(file)">
                <FileIcon :file="file" :size="30" ></FileIcon>&nbsp;{{ file.name }}
                  
                <span class="tag m-1">
                    <strong>Type:</strong>&nbsp;{{ file.mime_type }}
                </span>
            </a>
            </template>
            <template v-if="files.length == 0">
                <span class="dropdown-item">No files</span>
            </template>
           
            
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
    document.getElementsByTagName("html")[0].addEventListener("click", this._clickOut);
    if (this.selected) {
        this.current_file = this.selected;
    }
  },
  unmounted() {
    document.getElementsByTagName("html")[0].removeEventListener("click", this._clickOut);
  },
  methods: {
    _close() {
        var self = this;
        if (self.active) {
            self.$refs['dropdownClass'].classList.remove('is-active');
            self.active = false;
        } 
    },
    _open() {
        var self = this;
        if (!self.active) {
            this.$refs['dropdownClass'].classList.add('is-active');
            this.active = true;
        }
    },
    _clickOut(e) {
        var self = this;
        if (self.$refs['dropdownClass'].contains(e.target)) {
            return;
        }
        self._close();
    },
    _toggle() {
        if (this.active) {
            this.$refs['dropdownClass'].classList.remove('is-active');
            this.active = false;
        } else {
            this.$refs['dropdownClass'].classList.add('is-active');
            this.active = true;
        }
    },
    onClick() {
        if (this.active) {
            this._close();
        } else {
            this._open();
        }
    },
    onSelect(file) {
        console.log(file);
        this.current_file = file;
        this.$emit('file_selected', file);
        this._close();
    }
  }
}
</script>