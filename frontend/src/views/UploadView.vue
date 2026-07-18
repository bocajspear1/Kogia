<script setup>
import JobWait from '@/components/JobWait.vue'
import Notifications from '@/components/general/Notifications.vue'
</script>

<template>
    <div class="container column is-10">
        <Notifications ref="notifications"></Notifications>
        
        <div id="add-details" v-if="stage == 'add'" class="box">
            <div class="field">
                <label class="label">Submission Name (required)</label>
                <div class="control">
                    <input class="input" type="text" ref="nameInput">
                </div>
            </div>
            <div class="field">
                <label class="label">Description (optional)</label>
                <div class="control">
                    <textarea class="textarea" ref="descriptionInput"></textarea>
                </div>
            </div>
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
                                    <button class="button is-primary" @click.stop.prevent="submitFiles" ref="submitButton" disabled>
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
        </div>
        
        <JobWait v-if="stage == 'wait'" ref="waitItem" :job_uuid="job_uuid" @jobdone="onJobDone" ></JobWait>
    </div>
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";

export default {
  data() {
    return {
        stage: "add",
        job_uuid: "",
        submission_uuid: "",
        file_list: [],
        dragging: false
    }
  },
  mounted() {
    document.body.addEventListener('dragenter', this.dragStart);
  },
  methods: {
    onJobDone(job_data) {
        this.$router.push({ name: 'JobCreate', params: { submission_uuid: this.submission_uuid } });
    },
    submitFiles(e) {

        let formData = new FormData();

        for (var i in this.file_list) {
            formData.append('files', this.file_list[i], this.file_list[i].name);
        }


        var self = this;

        var name = self.$refs.nameInput.value;
        formData.append('name', name);
        var description = self.$refs.descriptionInput.value;
        formData.append('description', description);


        api.api_post_form('/submission/new', formData, function(response){
            console.log('SUCCESS!!', response);
            var resp_data = response;

            var job_uuid = resp_data['job_uuid'];
            self.job_uuid = job_uuid;
            self.submission_uuid = resp_data['submission_uuid'];
            self.stage = "wait";
        }, function(status, error){
            self.$refs.notifications.addNotification("error", "Upload Error: " + error['detail']);
        })
    },
    onFileChange(e) {
        this.dragEnd();
        var file_array = [...this.$refs.submissionfile.files];
        console.log(file_array)
        for (var i in file_array) {
            this.file_list.push(file_array[i])
        }
        if (this.file_list.length >= 1) {
            this.$refs.submitButton.disabled = false;
        } else {
            this.$refs.submitButton.disabled = true;
        }
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
  }
}
</script>