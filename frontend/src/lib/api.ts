const API_URL =
  import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1";

export const TOKEN_KEY = "kyhc_token";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

type QueryValue = string | number | boolean | undefined | null;

export function buildQuery(
  params: Record<string, QueryValue>,
): string {
  const search = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }

    search.set(key, String(value));
  }

  const query = search.toString();

  return query ? `?${query}` : "";
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();

  const headers = new Headers(options.headers);

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;

    try {
      const body = await response.json();

      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail) && body.detail[0]?.msg) {
        detail = body.detail[0].msg;
      }
    } catch {
      // Keep the default message.
    }

    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  get<T>(path: string): Promise<T> {
    return request<T>(path);
  },

  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "POST",
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  },

  put<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "PUT",
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  },

  delete<T = void>(path: string): Promise<T> {
    return request<T>(path, { method: "DELETE" });
  },
};

export async function loginRequest(
  email: string,
  password: string,
): Promise<string> {
  const form = new URLSearchParams({
    username: email,
    password,
  });

  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form.toString(),
  });

  if (!response.ok) {
    let detail = "Incorrect email or password";

    try {
      const body = await response.json();

      if (typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // Keep the default message.
    }

    throw new ApiError(response.status, detail);
  }

  const data = (await response.json()) as { access_token: string };

  return data.access_token;
}
