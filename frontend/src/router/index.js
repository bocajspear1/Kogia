import { createWebHistory, createRouter } from 'vue-router';
import Home from "@/views/Home.vue";
import Submissions from "@/views/Submissions.vue";
import Upload from "@/views/Upload.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/submissions",
    name: "Submissions",
    component: Submissions,
  },
  {
    path: "/upload",
    name: "Upload",
    component: Upload,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;