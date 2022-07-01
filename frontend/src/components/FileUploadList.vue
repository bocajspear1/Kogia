<template>
    <form>
        <div class="navbar is-light" @drop.prevent="onDrop" @dragend.prevent="dragEnd" @dragstart.prevent="dragStart" @dragenter.prevent="dragOnto" @dragleave.prevent="dragOff" @dragover.prevent="dragOnto" ref="topBar">
            <div class="navbar-menu">
                <div class="navbar-start">
                    <div class="navbar-item">
                        <div class="file">
                            <label class="file-label">
                                <input ref="submissionfile" class="file-input" type="file" name="submissionfile" multiple @change="onFileChange">
                                <span class="file-cta">
                                    <span class="file-icon">
                                        <mdicon name="plus" /> 
                                    </span>
                                    <span class="file-label">
                                        Choose a file…
                                    </span>
                                </span>
                            </label>
                        </div>
                    </div>
                    <div class="navbar-item" v-if="dragging">
                        Drag file here
                    </div>
                   
                </div>

                <div class="navbar-end">
                    <div class="navbar-item">
                        <div class="buttons">
                            <button class="button is-primary" @click.stop.prevent="submitFiles" ref="submitButton">
                                <mdicon name="cloud-upload-outline" /> &nbsp;&nbsp;Upload
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </form>
    


    <table class="table is-fullwidth" v-if="file_list.length > 0">
        <thead>
            <tr>
                <th>Name</th>
                <th>Filetype</th>
                <th>Size</th>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <th>Name</th>
                <th>Filetype</th>
                <th>Size</th>
            </tr>
        
        </tfoot>

        <tbody>
            <tr v-for="fileitem in file_list">
                <td>{{ fileitem['name'] }}</td>
                <td>{{ fileitem['type'] }}</td>
                <td>{{ fileitem['size'] }}</td>
            </tr>
        </tbody>
    </table>
    <div class="notification is-info" v-else>
        Add file above, or drag a file onto the bar
    </div>
</template>

<style scoped>

</style>

<script>
export default {
  data() {
    return {
      file_list: [],
      dragging: false
    }
  },
  emits: ["uploadfiles"],
  mounted() {
    document.body.addEventListener('dragenter', this.dragStart);
  },
  methods: {
    onFileChange(e) {
        this.dragEnd();
        var file_array = [...this.$refs.submissionfile.files];
        console.log(file_array)
        for (var i in file_array) {
            this.file_list.push(file_array[i])
        }
        console.log(this.file_list)
    },
    onDrop(e) {
        console.log("file dropped")
        var file_array = [...e.dataTransfer.files];
        console.log(file_array)
        for (var i in file_array) {
            this.file_list.push(file_array[i])
        }
        console.log(this.file_list)
        this.dragEnd();
    },
    dragStart(e){
        this.$refs.topBar.classList.add('is-warning')
        this.$refs.topBar.classList.remove('is-light')
        this.$refs.topBar.classList.remove('is-danger')
        this.dragging = true;
    },
    dragOnto(e){
        this.$refs.topBar.classList.add('is-danger')
        this.$refs.topBar.classList.remove('is-light')
        this.$refs.topBar.classList.remove('is-warning')
    },
    dragOff(e){
        this.$refs.topBar.classList.add('is-warning')
        this.$refs.topBar.classList.remove('is-danger')
        this.$refs.topBar.classList.remove('is-light')
    },
    dragEnd(e){
        console.log("end")
        this.$refs.topBar.classList.add('is-light')
        this.$refs.topBar.classList.remove('is-danger')
        this.$refs.topBar.classList.remove('is-warning')
        this.dragging = false;
    },
    submitFiles(e) {
        // this.$refs.submitButton.classList.add('is-loading');

        this.$emit('uploadfiles', this.file_list);
    }
  }
}
</script>
