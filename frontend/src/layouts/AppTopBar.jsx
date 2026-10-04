import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bell, ChevronDown, Search } from "lucide-react";
import api, { assetUrl } from "../shared/api/client";
import "./AppTopBar.css";

export default function AppTopBar({ search, setSearch }) {
  const [user, setUser] = useState(null);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/users/me").then(({ data }) => setUser(data)).catch(() => {});
  }, []);

  useEffect(() => {
    function closeProfile(event) {
      if (profileRef.current && !profileRef.current.contains(event.target)) setProfileOpen(false);
    }
    document.addEventListener("mousedown", closeProfile);
    return () => document.removeEventListener("mousedown", closeProfile);
  }, []);

  function logout() {
    localStorage.removeItem("token");
    navigate("/");
  }

  return (
    <header className="app-topbar">
      <label className="app-topbar-search">
        <Search size={19} aria-hidden="true" />
        <input
          type="search"
          aria-label="Search dashboard"
          placeholder="Search..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </label>
      <div className="app-topbar-actions">
        <div className="app-topbar-notifications">
          <button
            type="button"
            className="app-topbar-icon"
            aria-label="Notifications"
            aria-expanded={notificationsOpen}
            onClick={() => setNotificationsOpen((open) => !open)}
          >
            <Bell size={19} />
            <span className="app-topbar-badge">3</span>
          </button>
          {notificationsOpen && (
            <div className="app-topbar-dropdown app-topbar-notification-list">
              <strong>Notifications</strong>
              <p>📨 Campaign “Summer Sale” sent</p>
              <p>👤 New contact subscribed</p>
              <p>📄 Template updated</p>
            </div>
          )}
        </div>
        <div className="app-topbar-profile" ref={profileRef}>
          <button
            type="button"
            className="app-topbar-user"
            aria-label="Open profile menu"
            aria-expanded={profileOpen}
            onClick={() => setProfileOpen((open) => !open)}
          >
            <img src={user?.avatar ? assetUrl(user.avatar) : "https://via.placeholder.com/80"} alt="" />
            <span>{user?.name || "User"}</span>
            <ChevronDown size={15} />
          </button>
          {profileOpen && (
            <div className="app-topbar-dropdown app-topbar-profile-list">
              <strong>{user?.name || "User"}</strong>
              <button type="button" onClick={() => navigate("/profile")}>Edit Profile</button>
              <button type="button" onClick={() => navigate("/settings")}>Settings</button>
              <button type="button" className="logout-item" onClick={logout}>Logout</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
