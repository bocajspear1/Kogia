import { createWebHistory, createRouter } from 'vue-router';
import HomeView from "@/views/HomeView.vue";
import SubmissionsView from "@/views/SubmissionsView.vue";
import UploadView from "@/views/UploadView.vue";
import SubmissionSingleView from "@/views/SubmissionSingleView.vue";
import PluginsView from "@/views/PluginsView.vue";
import PluginSingleView from "@/views/PluginSingleView.vue";
import FileSingleView from "@/views/FileSingleView.vue";
import JobCreateView from "@/views/JobCreateView.vue";
import JobsView from "@/views/JobsView.vue";
import JobSingleView from "@/views/JobSingleView.vue";
import LoginView from "@/views/LoginView.vue";
import ExploreView from "@/views/ExploreView.vue";
import UserGuideView from "@/views/UserGuideView.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomeView,
  },
  {
    path: "/submissions",
    name: "Submissions",
    component: SubmissionsView,
  },
  {
    path: "/upload",
    name: "Upload",
    component: UploadView,
  },
  {
    path: "/submission/:submission_uuid",
    name: "SubmissionSingle",
    component: SubmissionSingleView,
  },
  {
    path: "/plugins",
    name: "Plugins",
    component: PluginsView,
  },
  {
    path: "/plugin/:plugin_name",
    name: "PluginSingle",
    component: PluginSingleView,
  },
  {
    path: "/file/:file_uuid",
    name: "FileSingle",
    component: FileSingleView,
  },
  {
    path: "/newjob/:submission_uuid",
    name: "JobCreate",
    component: JobCreateView,
  },
  {
    path: "/jobs",
    name: "Jobs",
    component: JobsView,
  },
  {
    path: "/explore",
    name: "Explore",
    component: ExploreView,
  },
  {
    path: "/job/:job_uuid/:page?",
    name: "JobSingle",
    component: JobSingleView,
  },
  {
    path: "/login",
    name: "LoginPage",
    component: LoginView,
  },
  {
    path: "/userguide/:page*",
    name: "UserGuide",
    component: UserGuideView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;