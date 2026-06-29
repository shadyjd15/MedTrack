# MediCal — Android wrapper (Capacitor)

This packages the **already-deployed** MediCal web app inside a native Android
shell, so it installs and behaves like a real app (its own icon, no browser
bar, access to native camera/file APIs) while still talking to your existing
Docker-deployed backend. It does **not** bundle a separate copy of the
frontend — `capacitor.config.ts` points the app at your live HTTPS URL, so
updating the web app updates everyone instantly with no app-store release.

## What you need (not available in the sandbox that generated this)
- Node.js 18+ and npm, with internet access
- Android Studio (includes the Android SDK) — https://developer.android.com/studio
- Your MediCal frontend deployed and reachable over **HTTPS** (a real domain
  with a TLS cert — e.g. via Caddy/Traefik/Let's Encrypt in front of the
  `frontend` container, or any reverse proxy you already use).

## One-time setup

```bash
cd android-app
npm install

# Point this at your real deployed HTTPS URL before anything else:
#   edit capacitor.config.ts -> server.url
npx cap add android
npx cap sync android
```

This generates a full native `android/` Gradle project next to this folder.

## Building an installable APK

```bash
npx cap open android
```

This opens the generated project in Android Studio. From there:
- **Build → Build Bundle(s) / APK(s) → Build APK(s)** for a debug/test APK
  you can install directly on a phone (`adb install app-debug.apk`) or share
  as a file.
- **Build → Generate Signed Bundle / APK** for a release build signed with
  your own keystore — required if you want to publish to the Play Store.

## Publishing to the Play Store (optional)

1. Create a [Google Play Console](https://play.google.com/console) developer
   account (one-time $25 fee).
2. Generate a signed `.aab` (Android App Bundle) via the signed-build flow above.
3. Create a new app listing, upload the `.aab`, fill in the store listing
   (screenshots, description, privacy policy URL — required since this app
   handles health data), and submit for review.

## Updating the app after a MediCal release

Because this wrapper loads your live URL rather than a bundled copy, **most**
updates (new pages, new features, bug fixes) need nothing here — they show up
the next time the app reloads, just like a website. You only need to rebuild
and re-publish this wrapper if you change:
- the app's name, icon, or splash screen,
- native plugin usage (e.g. adding a new native API),
- `capacitor.config.ts` itself (e.g. changing the server URL).

## Native camera/file access (optional next step)

`@capacitor/camera` is already listed as a dependency. To make the existing
"capture medicine/prescription photo" inputs use the native camera picker
instead of the browser's `<input type="file" capture>` (which already works
reasonably well in a WebView, but the native picker is smoother), you'd swap
those inputs for calls to `Camera.getPhoto()` from `@capacitor/camera` in the
relevant pages (`medicines.html`, `visits.html`, `lab-tests.html`,
`vaccinations.html`) when running inside the Capacitor shell. This is a
follow-up enhancement, not required to get a working APK.
