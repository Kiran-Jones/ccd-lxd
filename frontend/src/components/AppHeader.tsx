"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

type ThemeMode = "system" | "light" | "dark";

function resolveSystemTheme(): "light" | "dark" {
  if (typeof window === "undefined") {
    return "light";
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(mode: ThemeMode): void {
  const nextTheme = mode === "system" ? resolveSystemTheme() : mode;
  document.documentElement.setAttribute("data-theme", nextTheme);
}

export function AppHeader(): JSX.Element {
  const [mode, setMode] = useState<ThemeMode>("system");

  useEffect(() => {
    const stored = window.localStorage.getItem("dccd-theme") as ThemeMode | null;
    const initialMode = stored ?? "system";
    setMode(initialMode);
    applyTheme(initialMode);

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      if ((window.localStorage.getItem("dccd-theme") as ThemeMode | null) === "system") {
        applyTheme("system");
      }
    };
    media.addEventListener("change", onChange);

    return () => media.removeEventListener("change", onChange);
  }, []);

  function updateMode(next: ThemeMode): void {
    setMode(next);
    window.localStorage.setItem("dccd-theme", next);
    applyTheme(next);
  }

  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="brand-wrap">
          <Image
            src="/assets/dccd-logo.png"
            alt="Dartmouth Center for Career Design"
            width={185}
            height={80}
            style={{ width: "auto", height: "56px" }}
            priority
          />
          <div>
            <strong className="brand-title">Career Design Diagnostic</strong>
            <span className="brand-subtitle">LXD: Learn. Experience. Design.</span>
          </div>
        </div>
        <button
          type="button"
          className="secondary-btn"
          data-theme-dark={mode === "dark" ? "true" : "false"}
          onClick={() => updateMode(mode === "dark" ? "light" : "dark")}
          aria-label="Toggle dark mode"
        >
          {mode === "dark" ? "Light Mode" : "Dark Mode"}
        </button>
      </div>
    </header>
  );
}
