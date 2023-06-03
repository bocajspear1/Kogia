<script setup>
import ProcessNodes from '@/components/host/ProcessNodes.vue'
import GenericDropdown from '@/components/generic/GenericDropdown.vue'
</script>

<template>
<GenericDropdown @item_selected="onSelect" colorClass="is-success" ref="intDropdown">
    <template v-slot:selected="selected">
        <mdicon name="cog-box" :size="30" />&nbsp;
        <span v-if="selected.selected == null" >
            &nbsp;&nbsp;Select Process
        </span>
        <span v-if="selected.selected != null">
            <span class="pathtext">{{ selected.selected.path }}</span> ({{ selected.selected.pid }})
        </span>
    </template>
    <template v-slot:dropcontent="dropcontent">
        <div class="menu nobreak p-2">
            <ProcessNodes :processes="processes" @child_selected="dropcontent.onSelect" :selected_process="getSelectedProcess()"></ProcessNodes>
        </div>
    </template>
</GenericDropdown>
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
  expose: ['clear'],
  props: {
    processes: Array,
    selected: null
  },
  mounted() {
    if (this.selected) {
        this.current_process = this.selected;
    }
  },
  unmounted() {
    
  },
  methods: {
    onSelect(file) {
        this.current_process = file;
        this.$emit('process_selected', file);
    },
    getSelectedProcess() {
        if (this.current_process != null) {
            return this.current_process.uuid;
        } else {
            return "NONE";
        }
    },
    clear() {
        this.$refs.intDropdown.clear();
    }
  }
}
</script>