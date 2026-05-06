export interface ApiError extends Error {
  status: number;
}

export function makeApiError(status: number, message: string): ApiError {
  const err = new Error(message) as ApiError;
  err.name = "ApiError";
  err.status = status;
  return err;
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({ detail: res.statusText }));
    throw makeApiError(res.status, (data as { detail?: string }).detail ?? res.statusText);
  }
  return res.json() as Promise<T>;
}
