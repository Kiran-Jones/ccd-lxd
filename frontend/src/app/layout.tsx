import type { Metadata } from "next";
import "@xyflow/react/dist/style.css";

import { AppHeader } from "@/components/AppHeader";
import { BackendHealthCheck } from "@/components/BackendHealthCheck";

import "./globals.css";

export const metadata: Metadata = {
  title: "DCCD Career Design Diagnostic",
  description: "Student diagnostic survey for activity recommendations at Dartmouth Center for Career Design.",
  icons: {
    icon: [
      { url: "/cropped-Dartmouth-College-Favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/cropped-Dartmouth-College-Favicon-192x192.png", sizes: "192x192", type: "image/png" },
    ],
    apple: "/cropped-Dartmouth-College-Favicon-180x180.png",
  },
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
