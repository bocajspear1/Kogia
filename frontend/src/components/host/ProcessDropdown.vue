<script setup>
import ProcessNodes from '@/components/host/ProcessNodes.vue'
</script>
<template>
<div class="dropdown" ref="dropdownClass">
    <div class="dropdown-trigger">
        <button class="button is-success is-light" aria-haspopup="true" aria-controls="dropdown-menu" @click="onClick">
            <mdicon name="cog-box" :size="30" />&nbsp;
            <span v-if="current_process == null" >
                &nbsp;&nbsp;Select Process
            </span>
            <span v-if="current_process != null">
                <span class="pathtext">{{ current_process.path }}</span> ({{ current_process.pid }})
            </span>
            <span class="icon is-small">
                <mdicon name="chevron-down" :size="30" />
            </span>
        </button>
    </div>
    <div class="dropdown-menu" id="dropdown-menu" role="menu">
        <div class="dropdown-content">
            <div class="menu nobreak p-2">
                <ProcessNodes :processes="processes" @child_selected="onSelect" :selected_process="getSelectedProcess()"></ProcessNodes>
            </div>
        </div>
    </div>
</div>
</template>

<style scoped>
    .nobreak {
        white-space: nowrap;
    }

    .pathtext{
        font-family: 'Courier New', Courier, monospace;
    }
</style>

<script>

export default {
  data() {
    return {
        current_process: null,
        active: false,
    }
  },
  emits: ["process_selected"],
  props: {
    processes: Array,
    selected: null
  },
  mounted() {
    document.getElementsByTagName("html")[0].addEventListener("click", this._clickOut);
    if (this.selected) {
        this.current_process = this.selected;
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
        this.current_process = file;
        this.$emit('process_selected', file);
        this._close();
    },
    getSelectedProcess() {
        if (this.current_process != null) {
            return this.current_process.uuid;
        } else {
            return "NONE";
        }
    }
  }
}
</script>