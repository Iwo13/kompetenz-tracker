import type { Configuration, PopupRequest } from '@azure/msal-browser';

// Echte IDs kommen aus .env (VITE_CLIENT_ID, VITE_TENANT_ID)
// Für lokale Entwicklung ohne Entra ID wird MSAL im Dummy-Modus betrieben.
export const msalConfig: Configuration = {
  auth: {
    clientId:    import.meta.env.VITE_CLIENT_ID    ?? 'dummy-client-id',
    authority:   `https://login.microsoftonline.com/${import.meta.env.VITE_TENANT_ID ?? 'common'}`,
    redirectUri: import.meta.env.VITE_REDIRECT_URI ?? 'http://localhost:5173',
  },
  cache: {
    cacheLocation:      'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

export const loginRequest: PopupRequest = {
  scopes: [`api://${import.meta.env.VITE_CLIENT_ID ?? 'dummy-client-id'}/access_as_user`],
};
