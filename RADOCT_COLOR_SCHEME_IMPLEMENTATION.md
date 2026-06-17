# RADOCT White & Blue Color Scheme Implementation Guide

## Overview
This guide will help you implement a consistent white and blue color scheme across your entire RADOCT application with the professional logo integration.

---

## Step 1: Update Global Color Variables

**File:** `frontend/src/styles/globals.css`

Replace the `:root` color variables with the following blue and white palette:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Blue & White Professional Theme */
    --background: 0 0% 100%;
    --foreground: 15 23% 26%;

    --card: 0 0% 100%;
    --card-foreground: 15 23% 26%;

    --popover: 0 0% 100%;
    --popover-foreground: 15 23% 26%;

    /* Primary Blue */
    --primary: 217 100% 40%;
    --primary-foreground: 0 0% 100%;

    /* Secondary Blue */
    --secondary: 217 32% 17.5%;
    --secondary-foreground: 0 0% 100%;

    --muted: 210 40% 96.1%;
    --muted-foreground: 215 16.3% 46.9%;

    --accent: 217 100% 40%;
    --accent-foreground: 0 0% 100%;

    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 100%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 217 100% 40%;

    --radius: 0.5rem;
  }

  .dark {
    --background: 217 32% 17.5%;
    --foreground: 0 0% 100%;

    --card: 217 32% 17.5%;
    --card-foreground: 0 0% 100%;

    --popover: 217 32% 17.5%;
    --popover-foreground: 0 0% 100%;

    --primary: 217 100% 50%;
    --primary-foreground: 217 32% 17.5%;

    --secondary: 217 32% 17.5%;
    --secondary-foreground: 0 0% 100%;

    --muted: 217 32% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;

    --accent: 217 100% 50%;
    --accent-foreground: 217 32% 17.5%;

    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 100%;

    --border: 217 32% 17.5%;
    --input: 217 32% 17.5%;
    --ring: 217 100% 50%;
  }
}
```

---

## Step 2: Update Dashboard Layout with Logo

**File:** `frontend/src/components/layout/dashboard-layout.tsx`

Replace the sidebar header section:

```tsx
{/* Sidebar header */}
<div className="flex h-16 items-center border-b border-blue-200 pl-4 bg-white">
  <Link
    href="/dashboard"
    className="flex items-center gap-3 hover:opacity-80 transition-opacity"
  >
    <img
      src="/doctome-logo.png"
      alt="RADOCT Logo"
      className="h-10 w-10"
    />
    <span className="text-xl font-bold text-blue-600">RADOCT</span>
  </Link>
</div>
```

---

## Step 3: Update Login Page

**File:** `frontend/src/app/login/page.tsx`

Complete replacement for professional blue & white design:

```tsx
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        throw new Error("Invalid credentials");
      }

      const data = await response.json();
      localStorage.setItem("token", data.token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-xl shadow-lg p-8 space-y-8">
          {/* Logo Section */}
          <div className="text-center">
            <img
              src="/doctome-logo.png"
              alt="RADOCT"
              className="h-16 w-auto mx-auto mb-2"
            />
            <h1 className="text-2xl font-bold text-blue-600">RADOCT</h1>
          </div>

          {/* Form Header */}
          <div className="text-center border-b-2 border-blue-600 pb-6">
            <h2 className="text-2xl font-bold text-gray-900">Welcome Back</h2>
            <p className="mt-2 text-sm text-gray-600">Sign in to your account</p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={loading}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Enter your username"
                  required
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-semibold text-gray-900">
                    Password
                  </label>
                  <Link href="/forgot-password" className="text-sm text-blue-600 hover:text-blue-700">
                    Forgot password?
                  </Link>
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="p-4 rounded-lg bg-red-50 text-red-700 text-sm font-medium">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">or</span>
            </div>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{" "}
              <Link href="/register" className="font-semibold text-blue-600 hover:text-blue-700">
                Create one
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
```

---

## Step 4: Update Register Page

**File:** `frontend/src/app/register/page.tsx`

Apply the same styling pattern as login page with registration fields.

---

## Step 5: Update Home Page

**File:** `frontend/src/app/page.tsx`

```tsx
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-4 py-24">
        {/* Hero Section */}
        <div className="text-center space-y-8 mb-24">
          <img
            src="/doctome-logo.png"
            alt="RADOCT"
            className="h-24 mx-auto mb-8"
          />
          <h1 className="text-6xl sm:text-7xl font-bold tracking-tight text-blue-600">
            RADOCT
          </h1>
          <p className="text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto font-light leading-relaxed">
            Advanced RAG-powered knowledge management platform
            <br />
            Powerful. Intuitive. Revolutionary.
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mt-12">
            <Link
              href="/register"
              className="px-8 py-4 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700 shadow-lg transition-all"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 bg-gray-100 text-gray-900 rounded-lg text-lg font-semibold hover:bg-gray-200 transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 mb-24">
          <div className="p-6 rounded-lg bg-blue-50 border border-blue-200">
            <h3 className="text-xl font-bold text-blue-900 mb-2">Knowledge Base</h3>
            <p className="text-gray-600">Manage and organize your documents efficiently</p>
          </div>
          <div className="p-6 rounded-lg bg-blue-50 border border-blue-200">
            <h3 className="text-xl font-bold text-blue-900 mb-2">AI Chat</h3>
            <p className="text-gray-600">Get instant answers powered by advanced AI</p>
          </div>
          <div className="p-6 rounded-lg bg-blue-50 border border-blue-200">
            <h3 className="text-xl font-bold text-blue-900 mb-2">API Access</h3>
            <p className="text-gray-600">Integrate with your existing systems easily</p>
          </div>
        </div>
      </div>
    </main>
  );
}
```

---

## Step 6: Update Dashboard Pages

Update all dashboard pages (Knowledge Base, Chat, API Keys) to use blue accents and white backgrounds:

**Key elements to update:**
- Buttons: Use `bg-blue-600 hover:bg-blue-700`
- Cards: Use `bg-white border border-blue-100`
- Headers: Use `text-blue-900` with `border-b-2 border-blue-600`
- Accents: Use `text-blue-600` for highlights

**Example for Knowledge Base page header:**
```tsx
<div className="space-y-8">
  <div className="flex justify-between items-center border-b-2 border-blue-600 pb-6">
    <div>
      <h2 className="text-3xl font-bold text-blue-900">Knowledge Bases</h2>
      <p className="text-gray-600 mt-2">Manage your knowledge bases and documents</p>
    </div>
    <Link
      href="/dashboard/knowledge/new"
      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
    >
      + New Knowledge Base
    </Link>
  </div>

  {/* Cards and content */}
  <div className="grid gap-6">
    {/* Use bg-white border border-blue-100 for cards */}
  </div>
</div>
```

---

## Color Reference

| Element | Color | Tailwind Class |
|---------|-------|-----------------|
| Primary Buttons | Blue | `bg-blue-600 hover:bg-blue-700` |
| Backgrounds | White | `bg-white` |
| Text Primary | Dark | `text-gray-900` |
| Text Secondary | Gray | `text-gray-600` |
| Borders | Light Blue | `border-blue-100` / `border-blue-200` |
| Accents | Blue | `text-blue-600` |
| Hover State | Light Blue | `bg-blue-50` |

---

## Implementation Checklist

- [ ] Update `globals.css` with new color variables
- [ ] Update Dashboard layout sidebar with logo and "RADOCT"
- [ ] Update Login page with new design
- [ ] Update Register page with new design
- [ ] Update Home page with RADOCT branding
- [ ] Update Knowledge Base page styling
- [ ] Update Chat page styling
- [ ] Update API Keys page styling
- [ ] Test all pages on desktop (1920x1080)
- [ ] Test all pages on mobile (375x667)
- [ ] Verify logo displays correctly on all pages
- [ ] Check that all buttons use blue color scheme
- [ ] Confirm responsive design works properly

---

## Quick Terminal Commands to Test

```bash
cd frontend
npm install
npm run dev
```

Then visit:
- `http://localhost:3000` - Home page
- `http://localhost:3000/login` - Login page
- `http://localhost:3000/register` - Register page
- `http://localhost:3000/dashboard` - Dashboard

---

## Logo Placement Summary

| Page | Logo Size | Location |
|------|-----------|----------|
| Home | 96px | Center, hero section |
| Login | 64px | Center, top of form |
| Register | 64px | Center, top of form |
| Dashboard Sidebar | 40px | Left, header |
| Navigation | 40px | Sidebar header |

---

## Notes

- Ensure the logo file exists at `frontend/public/doctome-logo.png`
- Use responsive images with proper alt text for accessibility
- Keep consistent padding and spacing throughout
- Test on multiple devices and browsers
- Clear browser cache (Ctrl+Shift+Delete) when testing

