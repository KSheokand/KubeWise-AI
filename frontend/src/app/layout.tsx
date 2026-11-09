import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KubeWise AI | Kubernetes Observability",
  description:
    "Intelligent Kubernetes Observability Platform with AI-powered infrastructure monitoring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}