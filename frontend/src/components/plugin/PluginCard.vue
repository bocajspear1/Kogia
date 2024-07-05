<script setup>
import DynamicOptions from '@/components/dynamic/DynamicOptions.vue';
</script>

<template>
    <div class="card">
        <div class="card-header has-background-white-ter">
            <template v-if="plugin.enabled == true">
                <p class="card-header-title">
                {{ plugin.name }}
                </p>
            </template>
            <template v-if="plugin.enabled == false">
                <p class="card-header-title has-text-grey-lighter">
                {{ plugin.name }}
                </p>
            </template>
           
            <button class="card-header-icon" aria-label="more options" @click="togglePlugin()" :title="'Enable/disable ' + plugin.name + ' plugin'">
                <span class="icon">
                    <mdicon name="check" :size="20" v-if="plugin.enabled == true" />
                    <mdicon name="close" :size="20" v-if="plugin.enabled == false" />
                </span>
            </button>
        </div>
        <div class="content" v-if="plugin.enabled == true && plugin.options.length > 0">
            <div class="box">
                <DynamicOptions :options="plugin.options" @onOptionChange="onOptionChange"></DynamicOptions>
            </div>
        
        </div>
    </div>
</template>

<style scoped>
    .card-header-icon {
        border: 1px solid gray;
    }

    .short-textbox {
        width: 50%;
    }
</style>

<script>
export default {
  data() {
    return {
      
    }
  },
  props: ["plugin"],
  mounted() {
    console.log(this.plugin)
  },
  methods: {
    togglePlugin() {
        this.plugin['enabled'] = !this.plugin['enabled'];

    },
    onOptionChange(new_options) {
        for (var i in this.plugin.options) {
            this.plugin.options[i].value = new_options[this.plugin.options[i].name];
        }
    }
  }
}
</script>