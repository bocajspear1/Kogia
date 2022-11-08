<template>
    <nav class="navbar is-light">
      <div class="navbar-brand">
        &nbsp;
        <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navbarBasicExample">
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>

      <div id="navbarBasicExample" class="navbar-menu">
        <div class="navbar-start">
          <div class="navbar-item">
            <div class="buttons">
              <slot name="main"></slot>
            </div>
          </div>
        </div>

        <div class="navbar-end">
          <div class="navbar-item">
            <div class="buttons">
              <slot name="right"></slot>
              &nbsp;
            </div>
          </div>
        </div>
      </div>
    </nav>
</template>

<style scoped>

</style>

<script>
export default {
  data() {
    return {
      
    }
  },
  emits: [''],
  props: [],
  mounted() {
    console.log(this.iconname)
  },
  methods: {
    
  }
}
</script>
