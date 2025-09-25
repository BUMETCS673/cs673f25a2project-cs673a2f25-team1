<template>
  <div class="sidebar">
    <!-- Logo -->
    <div class="logo">
      <div class="logo-icon">
        <div class="logo-shape logo-shape-1"></div>
        <div class="logo-shape logo-shape-2"></div>
      </div>
      <span class="logo-text">Asset Management</span>
    </div>

    <!-- Navigation -->
    <nav class="nav">
      <!-- HOME Section -->
      <div class="nav-section">
        <h3 class="nav-section-title">HOME</h3>
        <ul class="nav-list">
          <li class="nav-item active">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </div>
              <span class="nav-text">Modern</span>
              <span class="nav-badge">New</span>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M3 3H21L19 21H5L3 3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <span class="nav-text">eCommerce</span>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </div>
              <span class="nav-text">Front Pages</span>
              <svg class="nav-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </li>
        </ul>
      </div>

      <!-- APPS Section -->
      <div class="nav-section">
        <h3 class="nav-section-title">APPS</h3>
        <ul class="nav-list">
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M21 16V8C21 6.9 20.1 6 19 6H5C3.9 6 3 6.9 3 8V16C3 17.1 3.9 18 5 18H19C20.1 18 21 17.1 21 16Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M7 10H17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M7 14H13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <span class="nav-text">Contact</span>
              <span class="nav-badge blue">2</span>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </div>
              <span class="nav-text">Blog</span>
              <svg class="nav-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M3 3H21L19 21H5L3 3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <span class="nav-text">E-Commerce</span>
              <svg class="nav-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </div>
              <span class="nav-text">Chats</span>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
              <span class="nav-text">Users Profile</span>
              <svg class="nav-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </div>
              <span class="nav-text">Invoice</span>
              <svg class="nav-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </div>
              <span class="nav-text">Notes</span>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                  <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                  <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                  <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
              <span class="nav-text">Calendar</span>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" stroke="currentColor" stroke-width="2"/>
                  <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
              <span class="nav-text">Email</span>
            </div>
          </li>
          <li class="nav-item">
            <div class="nav-item-content">
              <div class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M2 9L12 2L22 9V20C22 20.5304 21.7893 21.0391 21.4142 21.4142C21.0391 21.7893 20.5304 22 20 22H4C3.46957 22 2.96086 21.7893 2.58579 21.4142C2.21071 21.0391 2 20.5304 2 20V9Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                  <polyline points="2,9 12,15 22,9" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
              <span class="nav-text">Tickets</span>
            </div>
          </li>
        </ul>
      </div>
    </nav>

    <!-- User Profile -->
    <div class="user-profile">
      <div class="user-avatar">
        <div class="avatar-placeholder">M</div>
      </div>
      <div class="user-info">
        <div class="user-name">Mathew</div>
        <div class="user-role">Designer</div>
      </div>
      <button class="logout-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <polyline points="16,17 21,12 16,7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>

<style scoped>
.sidebar {
  width: 280px;
  height: 100vh;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
}

.logo {
  display: flex;
  align-items: center;
  padding: 24px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.logo-icon {
  position: relative;
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.logo-shape {
  position: absolute;
  border-radius: 4px;
}

.logo-shape-1 {
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  top: 0;
  left: 0;
}

.logo-shape-2 {
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, #06B6D4, #0891B2);
  bottom: 0;
  right: 0;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.nav {
  flex: 1;
  padding: 24px 0;
  overflow-y: auto;
}

.nav-section {
  margin-bottom: 32px;
}

.nav-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 16px 20px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0 12px 4px;
}

.nav-item-content {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.nav-item:hover .nav-item-content {
  background: #f8fafc;
}

.nav-item.active .nav-item-content {
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  color: white;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 12px;
  color: #6b7280;
}

.nav-item.active .nav-icon {
  color: white;
}

.nav-text {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.nav-item.active .nav-text {
  color: white;
}

.nav-badge {
  background: #E5E7EB;
  color: #6b7280;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.nav-badge.blue {
  background: #3B82F6;
  color: white;
}

.nav-item.active .nav-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-arrow {
  margin-left: 8px;
  color: #9ca3af;
}

.user-profile {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
  margin: 0 12px 12px;
  border-radius: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.avatar-placeholder {
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
}

.logout-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #f3f4f6;
  color: #374151;
}
</style>
