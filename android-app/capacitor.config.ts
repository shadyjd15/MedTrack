import { CapacitorConfig } from "@capacitor/cli";

// IMPORTANT: change `server.url` to the real HTTPS address of your deployed
// MediCal frontend (e.g. https://medical.yourdomain.com). Capacitor will load
// that live site inside the native shell rather than bundling a copy of the
// frontend, so this app always reflects the same server everyone else uses —
// no separate build/release needed when you update the web app.
//
// This MUST be HTTPS in production. Android blocks plain HTTP from a packaged
// app by default (and rightly so, given this app handles medical records).
const config: CapacitorConfig = {
  appId: "com.medical.app",
  appName: "MediCal",
  webDir: "www", // unused while server.url is set, but required by the CLI
  server: {
    url: "https://medical.yourdomain.com",
    cleartext: false,
    androidScheme: "https",
  },
  android: {
    backgroundColor: "#0B1A4D",
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 800,
      backgroundColor: "#0B1A4D",
      androidSplashResourceName: "splash",
      showSpinner: false,
    },
  },
};

export default config;
