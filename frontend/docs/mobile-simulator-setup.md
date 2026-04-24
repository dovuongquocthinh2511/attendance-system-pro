# Mobile Simulator Setup & PWA Installation Guide

> Guide for testing **Bestmix Pro HR** PWA on mobile simulators/emulators.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Option A: Chrome DevTools Device Mode (Quickest)](#2-option-a-chrome-devtools-device-mode)
3. [Option B: Android Emulator (Android Studio)](#3-option-b-android-emulator-android-studio)
4. [Option C: Physical Device via USB/Wi-Fi](#4-option-c-physical-device-via-usbwi-fi)
5. [Option D: iOS Testing (Safari Web Inspector)](#5-option-d-ios-testing)
6. [Installing the PWA on Device](#6-installing-the-pwa-on-device)
7. [Debugging & Testing Checklist](#7-debugging--testing-checklist)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

### Start the Dev Server

```bash
cd frontend
npm run dev
# App runs at http://localhost:3000
```

### Or Test Production Build (Recommended for PWA)

```bash
cd frontend
npm run build
npm run preview
# App runs at http://localhost:4173
```

> **Important**: Service workers and PWA install prompts only work reliably on:
> - `localhost` (any port)
> - HTTPS domains
>
> The production build (`npm run preview`) is recommended for testing PWA features like install prompts and service worker caching.

---

## 2. Option A: Chrome DevTools Device Mode

**Best for**: Quick responsive testing, no install required.

### Steps

1. Open Chrome, navigate to `http://localhost:3000` (dev) or `http://localhost:4173` (preview)
2. Press `F12` to open DevTools
3. Click the **Toggle Device Toolbar** icon (phone/tablet icon) or press `Ctrl + Shift + M`
4. Select a device preset from the dropdown:
   - **iPhone 14 Pro** (390 x 844)
   - **Samsung Galaxy S20** (360 x 800)
   - **iPad Air** (820 x 1180)
   - Or add custom dimensions
5. Enable touch simulation (enabled by default in device mode)

### Test PWA Features in DevTools

| Feature | How to Test |
|---------|-------------|
| **Service Worker** | DevTools → Application → Service Workers |
| **Manifest** | DevTools → Application → Manifest |
| **Cache Storage** | DevTools → Application → Cache Storage |
| **Offline Mode** | DevTools → Network → check "Offline" |
| **Slow Network** | DevTools → Network → Throttling → "Slow 3G" |
| **Geolocation** | DevTools → Sensors → Override location |
| **Install Prompt** | DevTools → Application → Manifest → "Install" button |

### Simulate GPS for Attendance Check-in

1. DevTools → Click `⋮` (three dots) → More tools → **Sensors**
2. Under **Location**, select "Other" and enter:
   - Latitude: `10.762622` (Ho Chi Minh City example)
   - Longitude: `106.660172`
3. Now the app's geolocation API will return these coordinates

---

## 3. Option B: Android Emulator (Android Studio)

**Best for**: Realistic Android testing, home screen install, push notifications.

### Step 1: Install Android Studio

1. Download from https://developer.android.com/studio
2. Run installer on Windows (not WSL)
3. During setup, check **Android Virtual Device (AVD)**
4. Complete the SDK setup wizard

### Step 2: Create a Virtual Device

1. Open Android Studio
2. Go to **Tools → Device Manager** (or **More Actions → Virtual Device Manager** from welcome screen)
3. Click **Create Virtual Device**
4. Choose a device:
   - **Pixel 7** or **Pixel 8** (recommended, modern specs)
   - Category: Phone
5. Select a system image:
   - **API 34 (Android 14)** or newer
   - Tab: **Recommended** → Download if needed
6. Name it (e.g., "Pixel 7 API 34") → **Finish**

### Step 3: Launch the Emulator

1. In Device Manager, click the **Play ▶** button next to your device
2. Wait for Android to boot (first time takes 1-2 minutes)

### Step 4: Connect to Your Dev Server

The Android emulator uses `10.0.2.2` to reach the host machine's `localhost`.

1. Open **Chrome** in the emulator
2. Navigate to: `http://10.0.2.2:3000` (dev) or `http://10.0.2.2:4173` (preview)
3. The app should load normally

> **If the connection fails**, check that your Windows Firewall allows inbound connections on ports 3000/4173. You may also need to run the dev server with `--host`:
> ```bash
> npm run dev -- --host
> # or
> npm run preview -- --host
> ```

### Step 5: Install PWA on Android Emulator

See [Section 6: Installing the PWA](#6-installing-the-pwa-on-device).

### Optional: ADB Port Forwarding

If `10.0.2.2` doesn't work, use ADB reverse:

```bash
# In Windows terminal (not WSL)
adb reverse tcp:3000 tcp:3000
adb reverse tcp:4173 tcp:4173
```

Now in the emulator, `http://localhost:3000` will work directly.

---

## 4. Option C: Physical Device via USB/Wi-Fi

**Best for**: Real-world testing on actual hardware.

### Method 1: Same Wi-Fi Network

1. Find your PC's local IP:
   ```bash
   # Windows CMD/PowerShell
   ipconfig
   # Look for IPv4 Address, e.g., 192.168.1.100
   ```
2. Start dev server with host binding:
   ```bash
   npm run dev -- --host
   # or
   npm run preview -- --host
   ```
3. On your phone's browser, navigate to: `http://192.168.1.100:3000`

### Method 2: USB + Chrome Remote Debugging (Android)

1. Enable **Developer Options** on your Android phone:
   - Settings → About Phone → tap "Build Number" 7 times
2. Enable **USB Debugging**:
   - Settings → Developer Options → USB Debugging → ON
3. Connect phone to PC via USB cable
4. On PC, open Chrome and navigate to `chrome://inspect/#devices`
5. Your device should appear. Click **Port forwarding** and add:
   - Port: `3000` → `localhost:3000`
   - Port: `4173` → `localhost:4173`
6. Check "Enable port forwarding"
7. On your phone's Chrome, navigate to `http://localhost:3000`

### Method 3: USB + Safari Web Inspector (iOS)

See [Section 5](#5-option-d-ios-testing).

---

## 5. Option D: iOS Testing

### Option D1: Safari on Mac (If Available)

If you have access to a Mac:

1. Install **Xcode** from App Store
2. Open Xcode → Settings → Platforms → Download iOS Simulator
3. Open Simulator: Xcode → Open Developer Tool → Simulator
4. Choose device: File → Open Simulator → iPhone 15 Pro
5. Open Safari in the simulator
6. Navigate to your dev server URL

### Option D2: Physical iPhone/iPad

1. Connect iPhone to a Mac via USB
2. On iPhone: Settings → Safari → Advanced → Web Inspector → ON
3. On Mac: Safari → Develop → [Your iPhone] → Select the page
4. Use Safari Web Inspector to debug

### Option D3: No Mac Available (Windows Only)

Since you're on Windows/WSL2, iOS simulator is not directly available. Alternatives:

- **BrowserStack** (https://www.browserstack.com) - Cloud-based real iOS devices (free trial)
- **LambdaTest** (https://www.lambdatest.com) - Similar cloud testing
- **Appetize.io** (https://appetize.io) - Upload web apps to run on iOS simulator in browser
- **Chrome DevTools** - Use iPhone device presets for layout testing (won't test Safari-specific PWA behavior)

> **Note**: iOS PWA behavior differs from Android:
> - iOS uses "Add to Home Screen" from Safari's Share menu (not Chrome)
> - iOS doesn't show the browser install banner automatically
> - iOS service worker support has limitations (no background sync, push notifications limited)

---

## 6. Installing the PWA on Device

### On Android (Emulator or Physical)

#### Method 1: Browser Install Banner

1. Open the app in **Chrome**: `http://10.0.2.2:3000` (emulator) or `http://<your-ip>:3000` (physical)
2. Chrome should show an **"Add to Home Screen"** or **"Install app"** banner at the bottom
3. Tap **Install**
4. The app icon "Bestmix" appears on the home screen
5. Launch it — it opens in standalone mode (no browser chrome)

#### Method 2: Chrome Menu Install

1. Open the app in Chrome
2. Tap the **⋮ (three dots)** menu in Chrome
3. Tap **"Install app"** or **"Add to Home Screen"**
4. Confirm the install
5. App appears on home screen with the Bestmix icon

#### Method 3: DevTools Install (Desktop Chrome)

1. Open DevTools → **Application** tab → **Manifest**
2. Click the **"Install"** link in the manifest section

### On iOS (Physical iPhone)

1. Open the app in **Safari** (PWA install only works in Safari on iOS)
2. Tap the **Share** button (square with arrow)
3. Scroll down and tap **"Add to Home Screen"**
4. Optionally edit the name → Tap **"Add"**
5. App appears on home screen with standalone display

### Verify PWA Installation

After installing, check these behaviors:

| Behavior | Expected |
|----------|----------|
| App opens without browser URL bar | Yes (standalone mode) |
| Status bar color | Dark navy (#1a1a2e) |
| App icon on home screen | Bestmix Pro HR icon |
| Orientation | Portrait locked |
| Splash screen | White background with app icon |
| Works after closing and reopening | Yes (cached by service worker) |

---

## 7. Debugging & Testing Checklist

### Functional Tests on Mobile

- [ ] **Login flow**: Enter credentials → redirects to Dashboard
- [ ] **Remember me**: Close and reopen → still logged in
- [ ] **Dashboard tiles**: Correct number based on role (employee: 4, manager: 6, admin: 7)
- [ ] **Attendance check-in**: GPS permission prompt → coordinates captured
- [ ] **Attendance check-out**: Timer shows duration → check-out succeeds
- [ ] **Leave request**: Date pickers work with touch → form submits
- [ ] **Pull-to-refresh**: Pull down on lists → data refreshes
- [ ] **Infinite scroll**: Scroll to bottom → more items load
- [ ] **Sidebar menu**: Hamburger tap → sidebar slides in → role-correct items
- [ ] **Offline banner**: Toggle airplane mode → orange banner appears
- [ ] **Back online**: Disable airplane mode → banner disappears, data refetches

### PWA-Specific Tests

- [ ] **Install prompt**: Banner appears or menu option available
- [ ] **Standalone mode**: No browser chrome after install
- [ ] **App icon**: Correct icon on home screen
- [ ] **Service worker**: Registered in DevTools → Application → Service Workers
- [ ] **Cache**: Static assets cached in Cache Storage
- [ ] **Offline shell**: Disconnect network → app shell still loads (shows offline banner)
- [ ] **Update flow**: Deploy new version → app auto-updates on next visit

### Remote Debugging (Android)

1. Connect device/emulator
2. Open `chrome://inspect/#devices` on desktop Chrome
3. Find your device and the app's page
4. Click **Inspect** → Full DevTools for the mobile page
5. Use Console, Network, Application tabs as usual

---

## 8. Troubleshooting

### "Site can't be reached" on Emulator

```bash
# Ensure dev server binds to all interfaces
npm run dev -- --host 0.0.0.0

# For emulator, use 10.0.2.2 instead of localhost
# For physical device, use your PC's LAN IP
```

### PWA Install Option Not Appearing

- Must be served over **HTTPS** or **localhost**
- Must have a valid **manifest.webmanifest** (check DevTools → Application → Manifest for errors)
- Must have a registered **service worker**
- Use `npm run build && npm run preview` instead of `npm run dev` for reliable PWA behavior
- Clear browser cache and try again

### Service Worker Not Registering

```
# Check browser console for errors
# Common fix: clear all site data
DevTools → Application → Storage → "Clear site data"
```

### GPS Not Working in Emulator

- **Android Emulator**: Click `⋯` (Extended Controls) → Location → Set coordinates manually
- **Chrome DevTools**: Sensors → Location → Set custom coordinates
- App needs location permission — accept the browser prompt

### Android Emulator Too Slow

- Enable **Hardware Acceleration**: Android Studio → SDK Manager → SDK Tools → Intel HAXM (or use Hyper-V)
- Allocate more RAM: Device Manager → Edit → Show Advanced → RAM: 4096 MB
- Use **x86_64** system image (not ARM) for better performance on x86 hosts

### WSL2-Specific Issues

Since you run the dev server in WSL2 but Android Studio runs on Windows:

```bash
# Option 1: Run dev server on Windows directly
cd /mnt/c/Users/Admin/Desktop/git-repo/attendance-system-pro/frontend
npm run dev -- --host

# Option 2: Find WSL2 IP and use it
hostname -I
# e.g., 172.25.123.45
# Then in emulator: http://172.25.123.45:3000

# Option 3: Port forwarding from Windows to WSL2
# In Windows PowerShell (Admin):
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=$(wsl hostname -I | cut -d' ' -f1)
```

---

## Quick Start (TL;DR)

**Fastest path to test on mobile simulator:**

```bash
# 1. Build & preview
cd frontend
npm run build && npm run preview -- --host

# 2. Open Chrome DevTools (F12) → Toggle Device Mode (Ctrl+Shift+M)
# 3. Select "iPhone 14 Pro" or "Pixel 7" preset
# 4. Test the app at http://localhost:4173

# For Android Emulator:
# Open http://10.0.2.2:4173 in Chrome on the emulator
```

**Fastest path to install PWA:**

1. Open app in Chrome (emulator/device)
2. Tap `⋮` menu → "Install app"
3. App appears on home screen in standalone mode
