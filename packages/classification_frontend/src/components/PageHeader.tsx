"use client";

import { usePathname } from "next/navigation";
import React from "react";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Badge } from "./ui/badge";
import { Label } from "./ui/label";
import { Separator } from "./ui/separator";
import { SidebarTrigger } from "./ui/sidebar";

export function PageHeader({
  data,
  children,
}: {
  data: { icon: any; heading: string; domain?: string };
  children?: Readonly<React.ReactNode>;
}) {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  // Format a segment for display (capitalize, replace hyphens with spaces)
  const formatSegment = (segment: string) =>
    segment
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

  return (
    <div className="sticky top-0 z-10">
      <div className="flex w-full flex-col gap-2 bg-white px-4 py-4">
        <div className="flex items-center gap-2">
          <SidebarTrigger className="-ml-1 px-1" />
          <Separator className="mr-2 h-4" orientation="vertical" />
          <Breadcrumb>
            <BreadcrumbList>
              {segments.length === 0 ? (
                // Root path - show the heading as breadcrumb page
                <BreadcrumbItem>
                  <BreadcrumbPage>{data.heading}</BreadcrumbPage>
                </BreadcrumbItem>
              ) : (
                segments.map((segment, index) => {
                  const href = `/${segments.slice(0, index + 1).join("/")}`;
                  const isLast = index === segments.length - 1;

                  return (
                    <React.Fragment key={segment}>
                      <BreadcrumbItem>
                        {isLast ? (
                          <div className="flex items-center gap-2">
                            <BreadcrumbPage>
                              {data.domain
                                ? formatSegment(data.domain)
                                : formatSegment(segment)}
                            </BreadcrumbPage>
                          </div>
                        ) : (
                          <>
                            <BreadcrumbLink href={href}>
                              {formatSegment(segment)}
                            </BreadcrumbLink>
                            <BreadcrumbSeparator />
                          </>
                        )}
                      </BreadcrumbItem>
                    </React.Fragment>
                  );
                })
              )}
            </BreadcrumbList>
          </Breadcrumb>
        </div>
      </div>
    </div>
  );
}
