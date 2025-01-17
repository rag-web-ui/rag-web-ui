"use client";

import { ChevronRight, Home } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const Breadcrumb = () => {
  const pathname = usePathname();

  const generateBreadcrumbs = () => {
    const paths = pathname.split("/").filter(Boolean);
    const breadcrumbs = paths.map((path, index) => {
      const href = "/" + paths.slice(0, index + 1).join("/");
      const label =
        path.charAt(0).toUpperCase() + path.slice(1).replace(/-/g, " ");
      const isLast = index === paths.length - 1;

      // Handle dynamic routes with [id]
      const displayLabel = path.match(/^\[.*\]$/) ? "Details" : label;

      return {
        href,
        label: displayLabel,
        isLast,
      };
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  if (pathname === "/") return null;

  return (
    <nav className="flex items-center space-x-2 text-base text-muted-foreground mb-6">
      <Link
        href="/dashboard"
        className="flex items-center hover:text-foreground transition-colors"
      >
        <Home className="h-4 w-4" />
      </Link>

      {breadcrumbs.map((breadcrumb, index) => (
        <div key={breadcrumb.href} className="flex items-center">
          <ChevronRight className="h-4 w-4 mx-2 text-muted-foreground/50" />
          {breadcrumb.isLast ? (
            <span className="text-foreground font-medium">
              {breadcrumb.label}
            </span>
          ) : (
            <Link
              href={breadcrumb.href}
              className="hover:text-foreground transition-colors"
            >
              {breadcrumb.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  );
};

export default Breadcrumb;
