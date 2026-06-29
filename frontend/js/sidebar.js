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
  vaccine: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18 3l3 3-2 2-1-1-7 7 1 1-2 2-1-1-2 2-2-2 2-2-1-1 2-2 1 1 7-7-1-1 2-2z"/><path d="M9.5 14.5l-3 3"/></svg>`,
  flask: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 2h6M10 2v7l-5.5 9a2 2 0 0 0 1.7 3h11.6a2 2 0 0 0 1.7-3L14 9V2"/><path d="M7 16h10"/></svg>`,
  report: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 17l2.5-3 3 2L18 11"/><rect x="3" y="3" width="18" height="18" rx="2"/></svg>`,
  sun: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/></svg>`,
  moon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5z"/></svg>`,
  allergy: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2L2 20h20L12 2z"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="17" r="0.6" fill="currentColor"/></svg>`,
};

function renderSidebar(activePage) {
  const user = Auth.getUser() || {};
  const isAdmin = user.role === "admin";

  const navItems = [
    { key: "dashboard", label: "Dashboard", href: "/dashboard.html", icon: ICONS.dashboard },
    { key: "medicines", label: "Medicines", href: "/medicines.html", icon: ICONS.pill },
    { key: "visits", label: "Doctor Visits", href: "/visits.html", icon: ICONS.visits },
    { key: "labtests", label: "Lab Tests & Imaging", href: "/lab-tests.html", icon: ICONS.flask },
    { key: "vaccinations", label: "Vaccinations", href: "/vaccinations.html", icon: ICONS.vaccine },
    { key: "allergies", label: "Allergies", href: "/allergies.html", icon: ICONS.allergy },
    { key: "search", label: "Search", href: "/search.html", icon: ICONS.search },
    { key: "reports", label: "Reports", href: "/reports.html", icon: ICONS.report },
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

  const isDark = document.documentElement.getAttribute("data-theme") === "dark";

  return `
  <aside class="sidebar" id="sidebar">
    <button class="collapse-btn" id="collapseBtn" title="Collapse sidebar">${ICONS.collapse}</button>
    <div class="sidebar-brand">
      <div class="logo-mark"><img src="/assets/logo.png" alt="MediCal logo" /></div>
      <div class="brand-name">MediCal</div>
    </div>
    <div id="patientSwitcherMount"></div>
    <nav class="sidebar-nav">${navHtml}</nav>
    <div class="sidebar-footer">
      <button class="theme-toggle" onclick="toggleTheme()">
        ${isDark ? ICONS.sun : ICONS.moon}<span class="nav-label" id="themeToggleLabel">${isDark ? "Light mode" : "Dark mode"}</span>
      </button>
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
      <div class="version-footer">
        <span id="versionLabel">v…</span>
        <span id="updatePill"></span>
      </div>
    </div>
  </aside>`;
}

function mountSidebar(activePage) {
  const mount = document.getElementById("sidebarMount");
  if (mount) mount.outerHTML = renderSidebar(activePage);
  const sidebar = document.getElementById("sidebar");

  // Desktop collapse (icon-only) toggle
  const btn = document.getElementById("collapseBtn");
  const COLLAPSE_KEY = "mt_sidebar_collapsed";
  if (localStorage.getItem(COLLAPSE_KEY) === "1") sidebar.classList.add("collapsed");
  btn.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    localStorage.setItem(COLLAPSE_KEY, sidebar.classList.contains("collapsed") ? "1" : "0");
  });

  // Mobile off-canvas drawer
  if (!document.querySelector(".mobile-menu-btn")) {
    const mobileBtn = document.createElement("button");
    mobileBtn.className = "mobile-menu-btn";
    mobileBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>`;
    document.body.appendChild(mobileBtn);

    const backdrop = document.createElement("div");
    backdrop.className = "sidebar-backdrop";
    document.body.appendChild(backdrop);

    const closeMobileNav = () => {
      document.getElementById("sidebar").classList.remove("mobile-open");
      backdrop.classList.remove("open");
    };
    mobileBtn.addEventListener("click", () => {
      document.getElementById("sidebar").classList.add("mobile-open");
      backdrop.classList.add("open");
    });
    backdrop.addEventListener("click", closeMobileNav);
    document.querySelectorAll(".nav-item").forEach(el => el.addEventListener("click", closeMobileNav));
  }

  checkVersion();
  mountPatientSwitcher();
}

async function checkVersion() {
  const label = document.getElementById("versionLabel");
  const pill = document.getElementById("updatePill");
  if (!label) return;
  try {
    const info = await apiRequest("/version");
    label.textContent = `v${info.version}`;
    label.title = "Current installed version";
    if (info.repo) {
      try {
        const ghRes = await fetch(`https://api.github.com/repos/${info.repo}/releases/latest`);
        if (ghRes.ok) {
          const gh = await ghRes.json();
          const latest = (gh.tag_name || "").replace(/^v/i, "");
          if (latest && latest !== info.version) {
            pill.innerHTML = `<span class="update-pill" title="Latest: v${latest}">Update available</span>`;
            pill.querySelector(".update-pill").addEventListener("click", () => window.open(gh.html_url || `https://github.com/${info.repo}/releases/latest`, "_blank"));
          }
        }
      } catch (e) { /* offline or repo not public yet — silently skip */ }
    }
  } catch (e) {
    label.textContent = "";
  }
}

async function mountPatientSwitcher() {
  const mount = document.getElementById("patientSwitcherMount");
  if (!mount) return;
  const user = Auth.getUser() || {};
  if (user.role !== "caregiver") { mount.innerHTML = ""; return; }

  try {
    const patients = await apiRequest("/caregivers/my-patients");
    if (!patients.length) {
      mount.innerHTML = `<div style="padding:8px 16px;font-size:11.5px;color:#7FA09D;">No patients linked yet. Ask your administrator.</div>`;
      return;
    }
    const activeId = localStorage.getItem("mt_active_patient") || patients[0].id;
    localStorage.setItem("mt_active_patient", activeId);
    mount.innerHTML = `
      <div style="padding:0 16px 12px;">
        <label style="font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:#5E7C7A;font-weight:700;display:block;margin-bottom:5px;">Viewing patient</label>
        <select id="patientSwitcherSelect" style="width:100%;padding:7px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.06);color:#fff;font-size:12.5px;">
          ${patients.map(p => `<option value="${p.id}" ${p.id === activeId ? "selected" : ""}>${p.full_name || p.username}</option>`).join("")}
        </select>
      </div>`;
    document.getElementById("patientSwitcherSelect").addEventListener("change", (e) => {
      localStorage.setItem("mt_active_patient", e.target.value);
      window.location.reload();
    });
  } catch (e) {
    mount.innerHTML = "";
  }
}
