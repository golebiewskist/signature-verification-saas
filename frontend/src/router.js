import { createRouter, createWebHistory } from 'vue-router';
import LoginView from './views/LoginView.vue';
import DashboardView from './views/DashboardView.vue';


const routes = [
    { path: '/login', component: LoginView },
    { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/:pathMatch(.*)*', redirect: '/login' }
];


const router = createRouter({
    history: createWebHistory(),
    routes
});


router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('accessToken');
    if (to.meta.requiresAuth && !token) next('/login');
    else next();
});


export default router;