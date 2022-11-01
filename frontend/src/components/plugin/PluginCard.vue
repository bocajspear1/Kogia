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
           
            <button class="card-header-icon" aria-label="more options" @click="togglePlugin()" :title="'Enable/disable ' + plugin.name + ' plugin'">
                <span class="icon">
                    <mdicon name="check" :size="20" v-if="plugin.enabled == true" />
                    <mdicon name="close" :size="20" v-if="plugin.enabled == false" />
                </span>
            </button>
        </div>
        <div class="content" v-if="plugin.enabled == true && plugin.options.length > 0">
            <div class="box">
            <template v-for="option in plugin.options">
                <div v-if="option.type == 'number'" class="field">
                    <label class="label">{{ option.description }}</label>
                    <div class="control">
                        <input class="input" type="text" :name="option.name" v-model="option.value" ref="pluginoptions">
                    </div>
                </div>
              
            </template>
            </div>
        
        </div>
    </div>
</template>

<style scoped>
    .card-header-icon {
        border: 1px solid gray;
    }
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
    console.log(this.plugin)
    for (var i = 0; i < this.plugin.options.length; i++) {
        this.plugin.options[i].value = this.plugin.options[i].default;
    }
  },
  methods: {
    togglePlugin() {
        this.plugin['enabled'] = !this.plugin['enabled'];

    }
  }
}
</script>