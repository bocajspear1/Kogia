<template>
    <div class="list has-hoverable-list-items">
        <div v-for="file in files" class="list-item is-clickable">
            <div class="list-item-image p-2">
            <template v-if="file.unpacked_archive == true">
                <mdicon name="archive" :size="40" />
            </template>
            <template v-else-if="file.exec_interpreter == 'powershell'">
                <mdicon name="powershell" :size="40" />
            </template>
            <template v-else-if="file.exec_interpreter == 'dotnet'">
                <mdicon name="dot-net" :size="40" />
            </template>
            <template v-else-if="file.target_os == 'windows'">
                <mdicon name="microsoft-windows" :size="40" />
            </template>
            <template v-else-if="file.exec_interpreter == 'native'">
                <mdicon name="file-cog" :size="40" />
            </template>
            <template v-else-if="file.exec_interpreter != '' && file.exec_interpreter != 'native'">
                <mdicon name="script" :size="40" />
            </template>
            <template v-else>
                <mdicon name="file-question" :size="40" />
            </template>
            </div>

            <div class="list-item-content">
                <div class="list-item-title">{{ file.name }}</div>
                <div class="list-item-description">
                    <span class="tag m-1">
                        <strong>Architecture:</strong>&nbsp;{{ file.exec_arch }}
                    </span>
                    <span class="tag m-1">
                        <strong>Bits:</strong>&nbsp;{{ file.exec_bits }}
                    </span>
                    <span class="tag m-1">
                        <strong>OS:</strong>&nbsp;{{ file.target_os }}
                    </span>
                    <span class="tag m-1">
                        <strong>Format:</strong>&nbsp;{{ file.exec_format }}
                    </span>
                    <span class="tag m-1" v-if="file.exec_packer != ''">
                        <strong>Packer:</strong>&nbsp;{{ file.exec_packer }}
                    </span>

                </div>
            </div>
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
  props: ["files"],
  mounted() {
    console.log(this.files)
  },
  methods: {
    
  }
}
</script>