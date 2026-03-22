# Frontend PWA Design - Bestmix Pro HR

**Date**: 2026-03-22
**Status**: Approved
**Approach**: Monolith SPA (React + Vite + PWA)

## Overview

Mobile-first Progressive Web App for Bestmix Pro HR system. Serves as the frontend layer connecting employees and managers to the FastAPI backend, which proxies HR operations to Odoo 18 ERP.

**Primary users**: Employee (check-in/out daily) + Manager (approve leave on mobile)
**Secondary users**: Admin (user management, responsive desktop acceptable)

## Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI Framework | Ant Design Mobile (antd-mobile) | HR-friendly components, professional look, mobile-native |
| State Management | React Context + TanStack Query | Context for auth/app state, TanStack Query for all API calls |
| Offline Strategy | Offline-aware only | App shell cached, all actions require online. Banner when offline |
| Navigation | Hamburger menu + Dashboard grid | Flexible for Manager's extra functions, dashboard overview |
| Language | English only | Simpler maintenance, professional |
| Auth UX | Login + Remember me | Token in localStorage (remember) or sessionStorage (session) |
| Architecture | Monolith SPA | < 20 screens, shared components, simple deploy |

## Tech Stack

### Dependencies
- `react` + `react-dom` (v19)
- `react-router-dom` (v7) - routing
- `antd-mobile` - UI components
- `@tanstack/react-query` - server state management
- `axios` - HTTP client
- `dayjs` - date handling

### Dev Dependencies
- `vite` + `@vitejs/plugin-react`
- `vite-plugin-pwa` - PWA support
- `typescript`

## Project Structure

```
frontend/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
├── public/
│   ├── favicon.svg
│   ├── apple-touch-icon.png
│   ├── pwa-192x192.png
│   ├── pwa-512x512.png
│   └── robots.txt
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── vite-env.d.ts
│   ├── api/
│   │   ├── client.ts               # Axios instance + interceptors
│   │   ├── auth.ts                 # Auth API calls
│   │   ├── attendance.ts           # Attendance API calls
│   │   ├── leave.ts                # Leave API calls
│   │   ├── profile.ts              # Profile API calls
│   │   └── users.ts                # User management API calls
│   ├── contexts/
│   │   ├── AuthContext.tsx          # Auth state (user, token, role, login/logout)
│   │   └── AppContext.tsx           # App-level state (online status, sidebar)
│   ├── hooks/
│   │   ├── useAuth.ts              # Auth context consumer
│   │   ├── useOnlineStatus.ts      # Navigator.onLine listener
│   │   └── useMediaQuery.ts        # Responsive breakpoint hook
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx        # Main layout (hamburger + sidebar + content)
│   │   │   ├── Sidebar.tsx          # Slide-out menu (role-filtered items)
│   │   │   └── OfflineBanner.tsx    # "No connection" banner
│   │   └── common/
│   │       ├── ProtectedRoute.tsx   # Auth guard + role check
│   │       ├── RoleGuard.tsx        # Role-based render wrapper
│   │       └── PageLoading.tsx      # Loading skeleton
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── ForgotPassword.tsx
│   │   ├── ResetPassword.tsx
│   │   ├── Dashboard.tsx            # Role-adaptive dashboard grid
│   │   ├── attendance/
│   │   │   ├── AttendanceStatus.tsx  # Check-in/out + live timer
│   │   │   └── AttendanceHistory.tsx # History list + monthly summary
│   │   ├── leave/
│   │   │   ├── LeaveRequest.tsx
│   │   │   ├── LeaveHistory.tsx
│   │   │   ├── LeaveBalance.tsx
│   │   │   └── PendingApprovals.tsx  # Manager only
│   │   ├── profile/
│   │   │   ├── ProfileView.tsx
│   │   │   └── ContractView.tsx
│   │   └── admin/
│   │       └── UserManagement.tsx
│   ├── types/
│   │   └── index.ts                 # TypeScript interfaces
│   └── utils/
│       ├── token.ts                 # Token storage helpers
│       └── format.ts                # Date/number formatters
```

## Routing

```
/login                    → Login.tsx (public)
/forgot-password          → ForgotPassword.tsx (public)
/reset-password           → ResetPassword.tsx (public)
/                         → Dashboard.tsx (protected - all roles)
/attendance               → AttendanceStatus.tsx (protected - all roles)
/attendance/history       → AttendanceHistory.tsx (protected - all roles)
/leave                    → LeaveBalance.tsx (protected - all roles)
/leave/request            → LeaveRequest.tsx (protected - all roles)
/leave/history            → LeaveHistory.tsx (protected - all roles)
/leave/pending            → PendingApprovals.tsx (protected - manager, admin)
/profile                  → ProfileView.tsx (protected - all roles)
/profile/contract         → ContractView.tsx (protected - all roles)
/admin/users              → UserManagement.tsx (protected - admin only)
```

## Authentication Flow

1. App init → `AuthContext` checks token in storage (localStorage first, then sessionStorage)
2. Token exists → decode JWT, check expiry → valid: set user state, redirect `/`
3. Token expired → call `POST /auth/refresh` → fail: clear token, redirect `/login`
4. Login success → save token (localStorage if "Remember me", sessionStorage otherwise) → redirect `/`
5. Logout → call `POST /auth/logout` → clear token → redirect `/login`

### Axios Interceptors

**Request**: Attach `Authorization: Bearer {token}` header.

**Response**:
- 401 + token exists → try `POST /auth/refresh` → success: retry original → fail: force logout
- Network error → suppress throw, `useOnlineStatus` handles UI
- Other errors → throw for TanStack Query to handle

### Token Storage

- `saveToken(token, rememberMe)`: rememberMe → localStorage, otherwise → sessionStorage
- `getToken()`: check localStorage first, then sessionStorage
- `clearToken()`: remove from both

## Dashboard (Role-Adaptive)

### Employee (4 tiles)
| Tile | Data Source | Content |
|------|-----------|---------|
| Attendance | `GET /attendance/status` | Status + working duration or "Not checked in" |
| Leave Balance | `GET /leave/balance` | Total remaining days |
| Leave Request | Static | "New request" action tile |
| Profile | From JWT/auth state | Name + job title |

### Manager (+ 2 tiles)
| Tile | Data Source | Content |
|------|-----------|---------|
| Pending Approvals | `GET /leave/pending` | Badge with count |
| Team | Static | "View team" action tile |

### Admin (+ 1 tile)
| Tile | Data Source | Content |
|------|-----------|---------|
| User Management | Static | "Manage users" action tile |

Dashboard queries run in parallel via TanStack Query.

## Feature Screens

### Attendance Module

**AttendanceStatus** (`/attendance`):
- Large status card at top
- Not checked in: green "CHECK IN" button
- Working: live timer (counting from check_in_time) + red "CHECK OUT" button
- On check-in/out: call `navigator.geolocation.getCurrentPosition()` for GPS
  - GPS denied → still allow check-in, location = null
  - Send `latitude`, `longitude` in request body
- After action: invalidate `attendance/status` query

**AttendanceHistory** (`/attendance/history`):
- Tab bar: "History" | "Summary"
- **History tab**: List with each record showing:
  - Date (e.g., "Mar 21, 2026")
  - Check-in time → Check-out time
  - Worked hours
  - Check-in/out GPS location (link to Google Maps: `https://maps.google.com/?q={lat},{lng}`)
  - Mode badge (manual / face_id)
  - Infinite scroll or "Load more"
- **Summary tab**: Monthly summary
  - Month/year picker
  - Total hours, attendance count
  - Progress indicator vs target

**GPS in History**: All users see their own location data. Manager viewing team attendance requires a new backend endpoint (noted as future enhancement).

### Leave Module

**LeaveBalance** (`/leave`):
- List of leave types with balance visualization
- Each type: name, progress bar (taken/allocated), remaining days
- "New Request" button at bottom

**LeaveRequest** (`/leave/request`):
- Form with antd-mobile components:
  - `Picker`: leave type (from `GET /leave/types`)
  - `DatePicker`: date_from (>= today), date_to (>= date_from)
  - `TextArea`: description (optional)
- Submit: `POST /leave/request` (create draft) → auto `POST /leave/{id}/confirm`
- Success: navigate to `/leave/history`

**LeaveHistory** (`/leave/history`):
- List with status badges (antd-mobile `Tag`):
  - draft → grey, confirm → orange "Pending", validate → green "Approved", refuse → red "Rejected"
- Each item: leave type, date range, number of days, status

**PendingApprovals** (`/leave/pending`) - Manager/Admin:
- List of requests with state = `confirm`
- Each item: employee name, leave type, date range, days count
- Two action buttons: Approve (green) / Reject (red)
- Confirm dialog before action
- After action: invalidate query, item removed from list

### Profile Module

**ProfileView** (`/profile`):
- Info card from Odoo (`GET /profile/`): name, job title, department, email, phone, birthday
- Edit mode: only 4 editable fields (mobile_phone, work_email, identification_id, birthday)
- antd-mobile Form with inline edit pattern
- Link to "View Contract"

**ContractView** (`/profile/contract`):
- Read-only card: contract name, wage, state, start/end dates, job, department
- State badge: open (green), draft (grey), close (red)

### Admin Module

**UserManagement** (`/admin/users`):
- List with search filter
- Each user: email, role badge, active status, odoo link indicator
- Pull-down refresh
- Floating "+" button → create user (antd-mobile Popup form)
- Tap item → edit form (same Popup)
- Swipe left → delete (with confirm dialog)

## Layout & Sidebar

**AppLayout** (wrapper for all protected pages):
- **Top bar**: hamburger (left) + page title (center) + avatar initial (right)
- **Sidebar**: antd-mobile `Popup` sliding from left
  - User info header: name, role badge, email
  - Menu items filtered by role:

| Item | Route | Roles |
|------|-------|-------|
| Dashboard | `/` | all |
| Attendance | `/attendance` | all |
| Attendance History | `/attendance/history` | all |
| Leave Balance | `/leave` | all |
| New Leave Request | `/leave/request` | all |
| Leave History | `/leave/history` | all |
| Pending Approvals | `/leave/pending` | manager, admin |
| Profile | `/profile` | all |
| User Management | `/admin/users` | admin |
| Logout | - | all |

- **OfflineBanner**: Fixed below top bar, yellow/orange, shown when `navigator.onLine === false`. Text: "No internet connection. Some features are unavailable."
- **Content area**: `<Outlet />`, scrolls independently

## PWA Configuration

```typescript
VitePWA({
  registerType: 'autoUpdate',
  manifest: {
    name: 'Bestmix Pro HR',
    short_name: 'Bestmix',
    description: 'HR Attendance & Leave Management',
    theme_color: '#1a1a2e',
    background_color: '#ffffff',
    display: 'standalone',
    orientation: 'portrait',
    scope: '/',
    start_url: '/',
    icons: [
      { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
      { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' }
    ]
  },
  workbox: {
    globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
    navigateFallback: 'index.html'
  },
  devOptions: {
    enabled: true,
    type: 'module',
    navigateFallback: 'index.html'
  }
})
```

## TanStack Query Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: true,
      networkMode: 'online'
    }
  }
})
```

## Error Handling

| Error Type | Handling |
|-----------|---------|
| API error (`success: false`) | `Toast.show({ icon: 'fail', content: error })` |
| Network error | OfflineBanner shown, no toast |
| 401 Unauthorized | Silent redirect to `/login` (after refresh fails) |
| 403 Forbidden | Toast "You don't have permission for this action" |
| Form validation | Inline error below field (antd-mobile Form rules) |

## Loading States

- **Page load**: Skeleton screen (`antd-mobile Skeleton`)
- **Button actions**: Loading spinner on button, disable double-tap
- **Lists**: `InfiniteScroll` or `PullRefresh` pattern
- **Dashboard tiles**: Individual skeleton per tile (parallel queries)

## Empty States

- No attendance history: "No records yet. Check in to start tracking."
- No leave history: "No leave requests yet."
- No pending approvals: "All caught up! No pending requests."

## Confirmation Patterns

- **Check-in/out**: Direct action (no confirm dialog)
- **Leave submit**: Direct submit (form has validation)
- **Approve/Reject leave**: `Dialog.confirm` - "Approve leave request for {name}?"
- **Delete user**: `Dialog.confirm` destructive - "Delete user {email}? This cannot be undone."
- **Logout**: Direct action

## Future Enhancements (Out of Scope)

- Manager viewing team attendance history (requires new backend endpoint)
- Planning/Schedule module integration (planning.slot)
- Biometric authentication (Web Authentication API)
- i18n multi-language support
- Offline queue for check-in/leave requests
