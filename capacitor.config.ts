import { CapacitorConfig } from '@capacitor/cli';
const config: CapacitorConfig = {
  appId: 'com.biomimetic.app',
  appName: 'Biomimetic',
  webDir: 'dist',
  server: { androidScheme: 'https' }
};
export default config;
