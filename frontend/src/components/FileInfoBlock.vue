<script setup>
import FileIcon from '@/components/FileIcon.vue'
</script>
<template>
    <div class="card">
    <div class="card-content">
        <div class="media">
            <div class="media-left">
                <figure class="image is-48x48">
                <FileIcon :file="file"></FileIcon>
                </figure>
            </div>
            <div class="media-content">
                <p class="title is-4">{{ file.name }}</p>
                <p class="subtitle is-6"><strong>SHA256: </strong>{{ file.hash }}</p>
            </div>
        </div>

        <div class="content">
            <div class="level">
                <div class="level-item has-text-centered">
                    <div>
                        <p class="title is-6 is-spaced">Type</p>
                        <p class="subtitle is-6">
                            {{ file.mime_type }}  
                        </p>
                    </div>
                </div>
                <div class="level-item has-text-centered">
                    <div>
                        <p class="title is-6 is-spaced">Format</p>
                        <p class="subtitle is-6">
                            {{ file.exec_format }}
                            <template v-if="file.exec_type">({{ file.exec_type }})</template>
                        </p>
                    </div>
                </div>
                <div class="level-item has-text-centered">
                    <div>
                        <p class="title is-6 is-spaced">Architecture</p>
                        <p class="subtitle is-6">{{ file.exec_arch }} 
                        <template v-if="file.exec_arch">(x{{ file.exec_bits }})</template></p>
                    </div>
                </div>
                <div class="level-item has-text-centered">
                    <div>
                        <p class="title is-6 is-spaced">OS</p>
                        <p class="subtitle is-6">{{ file.target_os }}</p>
                    </div>
                </div>
                <div class="level-item has-text-centered">
                    <div>
                        <p class="title is-6 is-spaced">Interpreter</p>
                        <p class="subtitle is-6">{{ file.exec_interpreter }}</p>
                    </div>
                </div>
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
      
    }
  },
  props: ["file"],
  mounted() {
    console.log(this.file)
  },
  methods: {
    
  }
}
</script>
