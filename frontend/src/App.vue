<script setup>
import { useUserSession } from '@/lib/store'
import router from '@/router'
let session = useUserSession();
</script>

<template>
  <header>
    <nav class="navbar is-dark" role="navigation" aria-label="main navigation">
      <div class="navbar-brand">
        <div class="navbar-item icon-item">
          <router-link to="/"><img rel="icon" :src="getNavImage()" /></router-link>
          
        </div>

        <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="kogiaNavbar">
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>

      <div id="kogiaNavbar" class="navbar-menu">
        <div class="navbar-start">
          <!-- <router-link class="navbar-item" to="/"><mdicon name="home" :size="20" />&nbsp;&nbsp;Home</router-link> -->
          <router-link class="navbar-item" to="/upload"><mdicon name="cloud-upload-outline" :size="20" />&nbsp;&nbsp;Upload</router-link>
          <router-link class="navbar-item" to="/submissions"><mdicon name="view-list-outline" :size="20" />&nbsp;&nbsp;Submissions</router-link>
          <router-link class="navbar-item" to="/jobs"><mdicon name="cog-outline" :size="20" />&nbsp;&nbsp;Jobs</router-link>
          <router-link class="navbar-item" to="/explore"><mdicon name="flask-empty" :size="20" />&nbsp;&nbsp;Explore</router-link>
          
        </div>

        <div class="navbar-end">
          <div class="navbar-item">
            <div class="navbar-item has-dropdown is-hoverable">
              <a class="navbar-link">
                <mdicon name="information" :size="20" />
              </a>

              <div class="navbar-dropdown is-right">
                <router-link class="navbar-item" to="/plugins"><mdicon name="video-input-component" :size="20" />&nbsp;&nbsp;Plugins</router-link>
                <hr class="navbar-divider">
                <router-link class="navbar-item" to="/userguide/index"><mdicon name="bookshelf" :size="20" />&nbsp;&nbsp;User Guide</router-link>
                <hr class="navbar-divider">
                <router-link class="navbar-item" to="/runners"><mdicon name="hammer" :size="20" />&nbsp;&nbsp;Runners</router-link>
              </div>
            </div>
          </div>
          <div class="navbar-item">
            <div class="navbar-item has-dropdown is-hoverable">
              <a class="navbar-link">
                <mdicon name="account" :size="20" />&nbsp;&nbsp;
                {{ session.username }}
              </a>

              <div class="navbar-dropdown is-right">
                <!-- <hr class="navbar-divider"> -->
                <a class="navbar-item">
                  Account
                </a>
                <a class="navbar-item" @click="logout">
                  Logout
                </a>
              </div>
            </div>
          </div>
        </div>

      </div>
      
    </nav>
  </header>
  <main class="main-content columns">
    <router-view />
  </main>
  <footer class="footer">
    <div class="content has-text-centered">
      <p>
        {{ getAppName() }} {{ version }}
      </p>
    </div>
  </footer>
</template>

<style>
.icon-item a img {
  vertical-align: middle;
}

</style>

<script>
import api from '@/lib/api';

export default {
  data() {
    return {
        version: "?"
    }
  },
  mounted() {
    var self = this;
    api.get_system_version(function(data) {
        self.version = data['version'];
    },
    function(status, data) {
        self.done = true;
        console.log('FAILURE!!', status, data);
    })
  },
  methods: {
    logout: function() {
      var self = this;
      let session = useUserSession();
      session.clearSession();
      router.push({ name: 'LoginPage'});
    },
    getNavImage() {
        return "/images/" + import.meta.env.VITE_IMAGE_PREFIX + "-navbar.png"
    },
    getAppName() {
        return import.meta.env.VITE_APP_NAME;
    },
  }
}
</script>