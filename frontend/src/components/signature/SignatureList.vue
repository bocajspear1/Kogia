<script setup>
import FileIcon from '@/components/file/FileIcon.vue'
</script>
<template>
    <div class="list has-hoverable-list-items has-visible-pointer-controls">
        <div v-for="signature in signatures" class="list-item" :ref="signature.uuid">
            <div class="list-item-image p-2">
                <mdicon v-if="signature.severity == '1'" name="information-variant" :size="30" />
                <mdicon v-if="signature.severity == '2'" name="help" :size="30" />
                <mdicon v-if="signature.severity == '3'" name="alert" :size="30" />
                <mdicon v-if="signature.severity == '4'" name="alert-octagon" :size="30" />
            </div>
            <div class="list-item-content">
                <div class="list-item-title">{{ signature.name }} ({{ signature.plugin }})</div>
                <div class="list-item-description">
                    {{ signature.description }}
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
        current: null
    }
  },
  emits: ["file_clicked"],
  props: {
    signatures: Array,
    toggle: Boolean
  },
  mounted() {
    
  },
  methods: {
    clickFile(uuid) {
        var toggled = false;
        if (this.toggle) {
            
            if (this.current == uuid) {
                this.$refs[uuid][0].classList.remove('has-background-grey-light');
                this.current = null;
                toggled = false;
            } else {
                if (this.current != null) {
                    this.$refs[this.current][0].classList.remove('has-background-grey-light');
                }
                this.$refs[uuid][0].classList.add('has-background-grey-light')
                this.current = uuid;
                toggled = true;
            }
        }
        var file_data = null;
        for (var i in this.files) {
            if (this.files[i].uuid == uuid) {
                file_data = this.files[i]
            }
        }
        this.$emit('file_clicked', uuid, file_data, toggled);
    }
  }
}
</script>