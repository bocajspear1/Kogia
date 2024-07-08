<script setup>
import { useUserSession } from '@/lib/store'
import router from '../router'
</script>

<template>
<div class="">
    <div class="modal is-active">
    <div class="modal-background"></div>
        <div class="modal-content">
            <div class="card">
                <div class="card-image has-text-centered">
                    <img class="image is-128x128 is-inline-block m-2" :src="getNavImage()"/>
                </div>
                <div class="card-content">
                    <div class="content">
                        <div class="field">
                            <label class="label">Username</label>
                            <div class="control has-icons-left has-icons-right">
                                <input class="input" type="text" ref="username">
                                <span class="icon is-small is-left">
                                    <mdicon name="account" :size="24" />
                                </span>
                            </div>
                        </div>
                        <div class="field">
                            <label class="label">Password</label>
                            <div class="control has-icons-left has-icons-right">
                                <input class="input" type="password" ref="password" @keyup.enter="login">
                                <span class="icon is-small is-left">
                                    <mdicon name="key" :size="24" />
                                </span>
                            </div>
                        </div>
                        <div class="field is-grouped">
                            <div class="control">
                                <button class="button is-link" @click="login">Login</button>
                            </div>
                        </div>
                        <div v-if="error_message != null" class="notification is-danger">
                            {{ error_message }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
</div>
    
</div>
  
</template>

<style scoped>
    .login-screen {
        z-index: 9999 !important;
        width: 100%;
        height: 100%;
        position: absolute;
    }
</style>


<script>
import api from '@/lib/api';

export default {
  data() {
    return {
       error_message: null,
    }
  },
  mounted() {
    
  },
  methods: {
    login() {
        var self = this;
        let session = useUserSession();
        self.error_message = null;
        api.do_login(self.$refs.username.value, self.$refs.password.value, 
            function(response){
                session.updateSession(self.$refs.username.value, response['api_key'], response['roles']);
                router.push({ name: 'Home'});
            },
            function(status_code, response){
                if (status_code == 401) {
                    self.error_message = "Login failed. Wrong username or password."
                } else {
                    self.error_message = "An error occcured. Please contact system administator."
                }   
            }
        )
    },
    getNavImage() {
        return "/images/" + import.meta.env.VITE_IMAGE_PREFIX + ".png"
    },
  }
}
</script>