const auth = Vue.reactive({
    token: localStorage.getItem("tma_token") || null,
    role: localStorage.getItem("tma_role") || null,
    name: localStorage.getItem("tma_name") || null,
    email: localStorage.getItem("tma_email") || null,

    isAuthed() {
        return !!this.token;
    },
    set(data) {
        this.token = data.token;
        this.role = data.role;
        this.name = data.name || "";
        this.email = data.email || "";
        localStorage.setItem("tma_token", this.token);
        localStorage.setItem("tma_role", this.role);
        localStorage.setItem("tma_name", this.name);
        localStorage.setItem("tma_email", this.email);
    },
    clear() {
        this.token = this.role = this.name = this.email = null;
        ["tma_token", "tma_role", "tma_name", "tma_email"].forEach(k => localStorage.removeItem(k));
    },
});

// Attach the auth token to every request
axios.interceptors.request.use(cfg => {
    if (auth.token) cfg.headers["Authentication-Token"] = auth.token;
    return cfg;
});

// If the token is rejected, log out and bounce to login
axios.interceptors.response.use(
    r => r,
    err => {
        if (err.response && err.response.status === 401 && auth.isAuthed()) {
            auth.clear();
            window.location.hash = "#/login";
        }
        return Promise.reject(err);
    }
);
