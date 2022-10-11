import { createWebHistory, createRouter } from 'vue-router';
import Home from "@/views/Home.vue";
import Submissions from "@/views/Submissions.vue";
import Upload from "@/views/Upload.vue";
import SubmissionSingle from "@/views/SubmissionSingle.vue";
import Plugins from "@/views/Plugins.vue";
import PluginSingle from "@/views/PluginSingle.vue";
import FileSingle from "@/views/FileSingle.vue";
import JobCreate from "@/views/JobCreate.vue";
import Jobs from "@/views/Jobs.vue";
import JobSingle from "@/views/JobSingle.vue";

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
  {
    path: "/submission/:submission_uuid",
    name: "SubmissionSingle",
    component: SubmissionSingle,
  },
  {
    path: "/plugins",
    name: "Plugins",
    component: Plugins,
  },
  {
    path: "/plugin/:plugin_name",
    name: "PluginSingle",
    component: PluginSingle,
  },
  {
    path: "/file/:file_uuid",
    name: "FileSingle",
    component: FileSingle,
  },
  {
    path: "/newjob/:submission_uuid",
    name: "JobCreate",
    component: JobCreate,
  },
  {
    path: "/jobs",
    name: "Jobs",
    component: Jobs,
  },
  {
    path: "/job/:job_uuid",
    name: "JobSingle",
    component: JobSingle,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;