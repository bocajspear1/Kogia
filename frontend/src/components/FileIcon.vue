<template>
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
