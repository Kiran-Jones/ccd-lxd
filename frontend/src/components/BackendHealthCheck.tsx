"use client";

import { useEffect } from "react";

import { pingBackendHealth } from "@/lib/api";

export function BackendHealthCheck(): null {
  useEffect(() => {
    void pingBackendHealth().catch(() => undefined);
  }, []);

  return null;
}
