const TrekkerDashboard = {
    template: `
    <div>
      <h3 class="text-success">Trekker Dashboard</h3>
      <p class="text-muted">Welcome, {{ auth.name }}. Browse & book treks starting in Milestone 5.</p>
      <div class="alert alert-info">You are logged in as <strong>Trekker</strong>.</div>
    </div>`,
    computed: { auth: () => auth },
};
