<script setup>

</script>

<template>
  <header>
    <nav class="navbar is-dark" role="navigation" aria-label="main navigation">
      <div class="navbar-brand">
        <div class="navbar-item">
          Kogia
        </div>

        <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="kogiaNavbar">
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>

      <div id="kogiaNavbar" class="navbar-menu">
        <div class="navbar-start">
          <router-link class="navbar-item" to="/"><mdicon name="home" :size="20" />&nbsp;&nbsp;Home</router-link>
          <router-link class="navbar-item" to="/upload"><mdicon name="cloud-upload-outline" :size="20" />&nbsp;&nbsp;Upload</router-link>
          <router-link class="navbar-item" to="/submissions"><mdicon name="view-list-outline" :size="20" />&nbsp;&nbsp;Submissions</router-link>
          
        </div>

      </div>
      
    </nav>
  </header>
  <main class="container">
    <router-view />
  </main>
</template>

<style>


</style>
