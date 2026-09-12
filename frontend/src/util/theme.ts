export type ThemeMode = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

export function getSystemTheme(): ResolvedTheme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

export function getResolvedTheme(mode: ThemeMode): ResolvedTheme {
  return mode === "system" ? getSystemTheme() : mode;
}

export function applyTheme(resolved: ResolvedTheme): void {
  document.documentElement.dataset.theme = resolved;
}

export function watchSystemTheme(callback: () => void): void {
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", callback);
}
