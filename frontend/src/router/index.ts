import { createRouter, createWebHistory} from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), //部署应用时的基本 URL。他由base 配置项决定
  routes: [
    /** 路由懒加载的方式 **/
    {
      path: "/aiChat",
      name: "aiChat",
      component: () => import("@/views/AiChatView.vue"),
    },
    {
      path: "/LaiChat",
      name: "LaiChat",
      component: () => import("@/views/LAiChatView.vue"),
    },
    // 主页（未登录 Landing Page）
    {
      path: "/",
      name: "home",
      component: () => import("@/views/Dashboard.vue"),
      meta: {
        title: "主页",
      },
    },
    // 登录后首页（仪表盘）
    {
      path: "/home",
      name: "homePage",
      component: () => import("@/views/HomeView.vue"),
      meta: {
        title: "首页",
      },
    },
    // 登录
    {
      path: "/login",
      name: "login",
      component: () => import('@/views/Login.vue')
    },
    //日历
    {
      path: "/calendar",
      name: "calendar",
      component: () => import('@/views/CalendarView.vue')
    },
    // 预算管理
    {
      path: "/budget",
      name: "budget",
      component: () => import('@/views/BudgetView.vue')
    },
    // 健康打卡
    {
      path: "/health",
      name: "health",
      component: () => import('@/views/HealthView.vue')
    },
    // 旅游规划
    {
      path: "/travel",
      name: "travel",
      component: () => import('@/views/TravelView.vue')
    },
    //主页
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import('@/views/Dashboard.vue')
    }
  ],
});

export default router;
