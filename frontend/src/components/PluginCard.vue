<script setup>

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
           
            <button class="card-header-icon" aria-label="more options" @click="togglePlugin()">
                <span class="icon">
                    <mdicon name="check" :size="20" v-if="plugin.enabled == true" />
                    <mdicon name="close" :size="20" v-if="plugin.enabled == false" />
                </span>
            </button>
        </div>
        <div class="content" v-if="plugin.enabled == true">
            Hi
        </div>
    </div>
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      
    }
  },
  props: ["plugin"],
  mounted() {
    
  },
  methods: {
    togglePlugin() {
        this.plugin['enabled'] = !this.plugin['enabled'];

    }
  }
}
</script>