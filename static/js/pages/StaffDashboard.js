const StaffDashboard = {
    template: `
    <div>
      <h3 class="text-success">Trek Staff Dashboard</h3>
      <p class="text-muted">Welcome, {{ auth.name }}. Your assigned treks arrive in Milestone 4.</p>
      <div class="alert alert-info">You are logged in as <strong>Trek Staff</strong>.</div>
    </div>`,
    computed: { auth: () => auth },
};
