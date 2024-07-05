<script setup>

</script>
<template>


<ul class="menu-list">
    <li v-for="process in processes">
        <a v-if="!selectable" @click="itemSelected(process)" :class="isActive(process.uuid)"><mdicon name="cog-box" :size="25" />&nbsp;
          <span class="pathtext">{{ process.path }}</span> ({{ process.pid }})
        </a>
        <span v-if="selectable">
          <!-- <mdicon name="cog-box" :size="25" /> -->
          <label class="checkbox m-4">
              <input type="checkbox" @input="itemChecked(process, $event.target.checked)" v-model="process_check[process.uuid]">
          </label>&nbsp;
          <span class="pathtext">{{ process.path }}</span> ({{ process.pid }})
        </span>
        <ProcessNode 
        v-if="process.child_processes.length > 0"
        :key="process.child_processes.id"
        :processes="process.child_processes"
        @child_selected="childSelected"
        @process_checked="childChecked"
        :selected_process="selected_process"
        :selectable="selectable"
        />
    </li>
</ul>
</template>

<style scoped>
  .pathtext{
    font-family: 'Courier New', Courier, monospace;
  }

  li {
    list-style-type: none;
  }
</style>

<script>
export default {
  name: "ProcessNode",
  data() {
    return {
        process_check: {},
    }
  },
  props: ['processes', 'selected_process', 'selectable'],
  emits: ["child_selected", "process_checked"],
  mounted() {
    var self = this;
  },
  methods: {
    childSelected(child) {
      this.$emit('child_selected', child);
    },
    itemSelected(child) {
      this.$emit('child_selected', child);
    },
    childChecked(child, value) {
      this.$emit('process_checked', child, value);
    },
    itemChecked(child, value) {
      this.$emit('process_checked', child, value);
    },
    isActive(uuid) {
      if (uuid == this.selected_process) {
        return "is-active";
      } else {
        return "";
      }
    }
  },
}
</script>
