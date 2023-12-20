<template>
<template v-if="file.unpacked_archive == true">
    <mdicon name="archive" :size="size" />
</template>
<template v-else-if="file.exec_interpreter == 'powershell'">
    <mdicon name="powershell" :size="size" />
</template>
<template v-else-if="file.exec_interpreter == 'dotnet'">
    <mdicon name="dot-net" :size="size" />
</template>
<template v-else-if="file.target_os == 'windows'">
    <mdicon name="microsoft-windows" :size="size" />
</template>
<template v-else-if="file.exec_interpreter == 'native'">
    <mdicon name="file-cog" :size="size" />
</template>
<template v-else-if="file.exec_interpreter != '' && file.exec_interpreter != 'native'">
    <mdicon name="script" :size="size" />
</template>
<template v-else-if="file.mime_type == 'text/plain'">
    <mdicon name="file-document" :size="size" />
</template>
<template v-else-if="file.mime_type == 'application/pdf'">
    <mdicon name="file-pdf-box" :size="size" />
</template>
<template v-else-if="file.mime_type.includes('application/vnd.openxmlformats-officedocument.spreadsheetml')">
    <mdicon name="file-excel" :size="size" />
</template>
<template v-else-if="file.mime_type.includes('application/vnd.openxmlformats-officedocument.wordprocessingml')">
    <mdicon name="file-word" :size="size" />
</template>
<template v-else-if="file.mime_type.startsWith('image/')">
    <mdicon name="file-image" :size="size" />
</template>
<template v-else>
    <mdicon name="file-question" :size="size" />
</template>
</template>

<style scoped>

</style>

<script>
export default {
  data() {
    return {
      
    }
  },
  props: {
    "file": Object,
    "size": {
        type: Number,
        default: 40
    }
  },
  mounted() {
    
  },
  methods: {
    
  }
}
</script>
