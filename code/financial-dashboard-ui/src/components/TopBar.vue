<template>
  <div class="topbar">
    <!-- Left Section -->
    <div class="topbar-left">
      <button class="menu-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <line x1="3" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2"/>
          <line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>
          <line x1="3" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2"/>
        </svg>
      </button>
      
      <button class="search-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <div class="nav-links">
        <button class="nav-link">
          Apps
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="nav-link">Chat</button>
        <button class="nav-link">Calendar</button>
        <button class="nav-link">Notes</button>
      </div>
    </div>

    <!-- Right Section -->
    <div class="topbar-right">
      <button class="action-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="currentColor" stroke-width="2"/>
        </svg>
      </button>

      <button class="action-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L15.09 8.26L22 9L17 14L18.18 21L12 17.77L5.82 21L7 14L2 9L8.91 8.26L12 2Z" stroke="currentColor" stroke-width="2"/>
        </svg>
      </button>

      <button class="cart-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M3 3H21L19 21H5L3 3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span class="cart-badge">0</span>
      </button>

      <button class="notification-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M18 8C18 6.4087 17.3679 4.88258 16.2426 3.75736C15.1174 2.63214 13.5913 2 12 2C10.4087 2 8.88258 2.63214 7.75736 3.75736C6.63214 4.88258 6 6.4087 6 8C6 15 3 17 3 17H21C21 17 18 15 18 8Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M13.73 21C13.5542 21.3031 13.3019 21.5547 12.9982 21.7295C12.6945 21.9044 12.3504 21.9965 12 21.9965C11.6496 21.9965 11.3055 21.9044 11.0018 21.7295C10.6981 21.5547 10.4458 21.3031 10.27 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="notification-badge"></span>
      </button>

      <div class="user-avatar">
        <div class="avatar-img">
          <div class="avatar-placeholder">M</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>

<style scoped>
.topbar {
  height: 70px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 280px;
  right: 0;
  z-index: 999;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.menu-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.search-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.search-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-left: 16px;
}

.nav-link {
  background: none;
  border: none;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 0;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link:hover {
  color: #3B82F6;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.cart-btn {
  position: relative;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.cart-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.cart-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #EF4444;
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
  line-height: 1.2;
}

.notification-btn {
  position: relative;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.notification-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.notification-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: #3B82F6;
  border-radius: 50%;
}

.user-avatar {
  cursor: pointer;
}

.avatar-img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.avatar-placeholder {
  color: white;
  font-weight: 600;
  font-size: 14px;
}
</style>
