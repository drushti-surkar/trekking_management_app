const AdminDashboard = {
    template: `
    <div>
      <h3 class="text-success">Admin Dashboard</h3>
      <p class="text-muted">Welcome, {{ auth.name }}. Full management tools arrive in Milestone 3.</p>
      <div class="alert alert-info">You are logged in as <strong>Admin</strong>.</div>
    </div>`,
    computed: { auth: () => auth },
};
