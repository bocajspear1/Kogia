<script setup>
import FileIcon from '@/components/file/FileIcon.vue'
</script>
<template>
<div class="dropdown" ref="dropdownClass">
    <div class="dropdown-trigger">
        <button class="button is-info is-light" aria-haspopup="true" aria-controls="dropdown-menu" @click="onClick">
        <mdicon name="application-braces" :size="25" />&nbsp;
        <span v-if="current_instance == null" >
            Select Execution Instance
        </span>
        <span v-if="current_instance != null">
            {{ current_instance.exec_module }} ({{ current_instance.start_time }})
        </span>
        <span class="icon is-small">
            <mdicon name="chevron-down" :size="30" />
        </span>
        </button>
    </div>
    <div class="dropdown-menu" id="dropdown-menu" role="menu">
        <div class="dropdown-content">
            <template v-if="instances.length != 0">
            <a v-for="instance in instances" class="dropdown-item" @click="onSelect(instance)">
                <mdicon name="microsoft-windows" :size="25" v-if="instance.run_os=='windows'"/>
                <mdicon name="file-cog" :size="25" v-if="instance.run_os=='linux'"/>
                {{ instance.exec_module }} ({{ instance.start_time }})
            </a>
            </template>
            <template v-if="instances.length == 0">
                <span class="dropdown-item">No Instances</span>
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
        current_instance: null,
        active: false,
    }
  },
  emits: ["execinst_selected"],
  props: {
    instances: Array,
    selected: null
  },
  mounted() {
    document.getElementsByTagName("html")[0].addEventListener("click", this._clickOut);
    if (this.selected) {
        this.current_instance = this.selected;
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
        this.current_instance = file;
        this.$emit('execinst_selected', file);
        this._close();
    }
  }
}
</script>