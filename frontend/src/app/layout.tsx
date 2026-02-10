import type { Metadata } from "next";
import "@xyflow/react/dist/style.css";

import { AppHeader } from "@/components/AppHeader";
import { BackendHealthCheck } from "@/components/BackendHealthCheck";

import "./globals.css";

export const metadata: Metadata = {
  title: "DCCD Career Design Diagnostic",
  description: "Student diagnostic survey for activity recommendations at Dartmouth Center for Career Design.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): JSX.Element {
  return (
    <html lang="en">
      <body>
        <BackendHealthCheck />
        <AppHeader />
        {children}
      </body>
    </html>
  );
}
