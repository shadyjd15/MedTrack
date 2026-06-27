const ICONS = {
  dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>`,
  pill: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="9" width="18" height="6" rx="3" transform="rotate(-45 12 12)"/><line x1="9.5" y1="9.5" x2="14.5" y2="14.5"/></svg>`,
  prescription: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M7 3h7l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M9 9h6M9 13h4"/><circle cx="9.5" cy="17" r="1.4"/></svg>`,
  search: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
  users: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="9" cy="8" r="3.2"/><path d="M2.5 20c0-3.5 2.9-6 6.5-6s6.5 2.5 6.5 6"/><circle cx="17.5" cy="8.5" r="2.6"/><path d="M16 13.5c2.7.4 4.5 2.4 4.5 5.5"/></svg>`,
  settings: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 13.5a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.9 2.9l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V20a2 2 0 1 1-4 0v-.2a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.9-2.9l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H4a2 2 0 1 1 0-4h.2a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.9-2.9l.1.1a1.7 1.7 0 0 0 1.9.3h0a1.7 1.7 0 0 0 1-1.6V4a2 2 0 1 1 4 0v.2a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.9 2.9l-.1.1a1.7 1.7 0 0 0-.3 1.9v0a1.7 1.7 0 0 0 1.6 1H20a2 2 0 1 1 0 4h-.2a1.7 1.7 0 0 0-1.5 1z"/></svg>`,
  visits: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/><path d="M12 13v4M10 15h4"/></svg>`,
  logout: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
  collapse: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>`,
  camera: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 8h3l2-3h6l2 3h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="3.5"/></svg>`,
};

function renderSidebar(activePage) {
  const user = Auth.getUser() || {};
  const isAdmin = user.role === "admin";

  const navItems = [
    { key: "dashboard", label: "Dashboard", href: "/dashboard.html", icon: ICONS.dashboard },
    { key: "medicines", label: "Medicines", href: "/medicines.html", icon: ICONS.pill },
    { key: "visits", label: "Doctor Visits", href: "/visits.html", icon: ICONS.visits },
    { key: "search", label: "Search", href: "/search.html", icon: ICONS.search },
  ];
  if (isAdmin) {
    navItems.push({ key: "users", label: "Manage Users", href: "/users.html", icon: ICONS.users });
  }
  navItems.push({ key: "settings", label: "Settings", href: "/settings.html", icon: ICONS.settings });

  const navHtml = navItems.map(item => `
    <a class="nav-item ${item.key === activePage ? "active" : ""}" href="${item.href}">
      ${item.icon}<span class="nav-label">${item.label}</span>
    </a>
  `).join("");

  return `
  <aside class="sidebar" id="sidebar">
    <button class="collapse-btn" id="collapseBtn" title="Collapse sidebar">${ICONS.collapse}</button>
    <div class="sidebar-brand">
      <div class="logo-mark">M</div>
      <div class="brand-name">MedTrack</div>
    </div>
    <nav class="sidebar-nav">${navHtml}</nav>
    <div class="sidebar-footer">
      <div class="user-chip">
        <div class="user-avatar">${initials(user.full_name || user.username)}</div>
        <div class="user-meta">
          <div class="uname">${user.full_name || user.username || ""}</div>
          <div class="urole">${user.role || ""}</div>
        </div>
      </div>
      <a class="nav-item" href="#" onclick="Auth.logout();return false;" style="margin-top:6px;">
        ${ICONS.logout}<span class="nav-label">Log out</span>
      </a>
    </div>
  </aside>`;
}

function mountSidebar(activePage) {
  const mount = document.getElementById("sidebarMount");
  if (mount) mount.outerHTML = renderSidebar(activePage);
  const btn = document.getElementById("collapseBtn");
  const sidebar = document.getElementById("sidebar");
  const COLLAPSE_KEY = "mt_sidebar_collapsed";
  if (localStorage.getItem(COLLAPSE_KEY) === "1") sidebar.classList.add("collapsed");
  btn.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    localStorage.setItem(COLLAPSE_KEY, sidebar.classList.contains("collapsed") ? "1" : "0");
  });
}
