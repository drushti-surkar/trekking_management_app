const routes = [
    { path: "/", redirect: () => (auth.isAuthed() ? "/" + auth.role : "/login") },
    { path: "/login", component: Login },
    { path: "/register", component: Register },
    { path: "/admin", component: AdminDashboard, meta: { role: "admin" } },
    { path: "/staff", component: StaffDashboard, meta: { role: "staff" } },
    { path: "/trekker", component: TrekkerDashboard, meta: { role: "trekker" } },
];

const router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes,
});

// Role-based access control guard
router.beforeEach(to => {
    // Already-authed users shouldn't see login/register
    if ((to.path === "/login" || to.path === "/register") && auth.isAuthed()) {
        return "/" + auth.role;
    }
    if (to.meta.role) {
        if (!auth.isAuthed()) return "/login";
        if (auth.role !== to.meta.role) return "/" + auth.role; // wrong role -> own dashboard
    }
    return true;
});
