const BYPASS_FLAG = "bypass_auth";

interface AuthConfig {
  bypass_auth: boolean;
}

interface BypassTokenResponse {
  access_token: string;
  token_type: string;
}

export function isBypassAuth(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  return sessionStorage.getItem(BYPASS_FLAG) === "true";
}

export async function ensureBypassSession(): Promise<boolean> {
  if (typeof window === "undefined") {
    return false;
  }

  try {
    const configResponse = await fetch("/api/auth/config");
    if (!configResponse.ok) {
      sessionStorage.removeItem(BYPASS_FLAG);
      return false;
    }

    const config: AuthConfig = await configResponse.json();
    if (!config.bypass_auth) {
      sessionStorage.removeItem(BYPASS_FLAG);
      return false;
    }

    sessionStorage.setItem(BYPASS_FLAG, "true");
    if (localStorage.getItem("token")) {
      return true;
    }

    const tokenResponse = await fetch("/api/auth/bypass-token");
    if (!tokenResponse.ok) {
      return false;
    }

    const data: BypassTokenResponse = await tokenResponse.json();
    if (!data.access_token) {
      return false;
    }

    localStorage.setItem("token", data.access_token);
    return true;
  } catch {
    return false;
  }
}
