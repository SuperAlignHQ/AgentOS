"use client";

import { Edit, MessageSquare, FileText, Plus } from "lucide-react";
import { StatusBadge } from "@/components/statusBadge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useApplications } from "@/hooks/useApplications";
import type { Application as ApiApplication } from "@/lib/apiTypes";
import { formatDate } from "@/lib/utils";

export interface Application extends ApiApplication {
  // Extending the API interface to maintain compatibility
  // The API interface already has all the required fields
}

interface ApplicationsTableProps {
  onApplicationClick?: (application: Application) => void;
  onCreateApplication?: () => void;
}

export function ApplicationsTable({
  onApplicationClick,
  onCreateApplication,
}: ApplicationsTableProps) {
  const { data, isLoading, isError, error } = useApplications();

  if (isLoading) {
    return (
      <div className="w-full overflow-hidden rounded-lg border border-border bg-card">
        <Table className="gap-2">
          <TableHeader>
            <TableRow className="h-[56px] w-[1392px] border-b bg-[#F5F5F5]">
              <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
                Application ID
              </TableHead>
              <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
                Date Added
              </TableHead>
              <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
                Document Check
              </TableHead>
              <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
                Policy Check
              </TableHead>
              <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
                System Status
              </TableHead>
              <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
                Underwriter Review
              </TableHead>
              <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
                Last Updated
              </TableHead>
              <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
                Updated By
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.from({ length: 5 }).map((_, index) => (
              <TableRow className="h-[56px] w-[1392px] border-b" key={index}>
                <TableCell>
                  <Skeleton className="h-4 w-24" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-20" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-16" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-16" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-16" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-16" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-20" />
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-6 w-6 rounded-full" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex h-48 items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Error loading applications</p>
          <p className="text-gray-500 text-sm">
            {error instanceof Error ? error.message : "Something went wrong"}
          </p>
        </div>
      </div>
    );
  }

  const applications = data?.applications || [];

  if (applications.length === 0) {
    return (
      <div className="w-full overflow-hidden rounded-lg border border-border bg-card">
        <div className="flex h-64 items-center justify-center">
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-lg font-semibold">No applications found</h3>
            <p className="mb-4 text-muted-foreground text-sm">
              There are no applications to review at the moment.
            </p>

          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full overflow-hidden rounded-lg border border-border bg-card">
      <Table className="gap-2">
        <TableHeader>
          <TableRow className="h-[56px] w-[1392px] border-b bg-[#F5F5F5]">
            <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
              Application ID
            </TableHead>

            <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
              Date Added
            </TableHead>
            <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
              Document Check
            </TableHead>

            <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
              Policy Check
            </TableHead>

            <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
              System Status
            </TableHead>
            <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
              Underwriter Review
            </TableHead>
            <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
              Last Updated
            </TableHead>
            <TableHead className="text-left font-normal text-black text-sm leading-[1.4] tracking-normal">
              Updated By
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {applications.map((app, index) => (
            <TableRow className="h-[56px] w-[1392px] border-b" key={index}>
              <TableCell>
                <div className="flex items-center gap-2">
                  <button
                    className="font-normal text-primary text-sm leading-[1.4] tracking-normal hover:underline"
                    onClick={() => onApplicationClick?.(app)}
                  >
                    {app.application_id}
                  </button>
                </div>
              </TableCell>

              <TableCell className="font-normal text-black text-sm leading-[1.4] tracking-normal">
                {formatDate(app.created_at)}
              </TableCell>
              <TableCell className="font-normal text-muted-foreground text-sm leading-[1.4] tracking-normal">
                <StatusBadge status={app.overall_document_check_status} />
              </TableCell>

              <TableCell className="font-normal text-black text-sm leading-[1.4] tracking-normal">
                <StatusBadge status={app.policy_check} />
              </TableCell>

              <TableCell className="font-normal text-black text-sm leading-[1.4] tracking-normal">
                <StatusBadge status={app.system_status} />
              </TableCell>
              <TableCell className="font-normal text-black text-sm leading-[1.4] tracking-normal">
                <StatusBadge status={app.underwriter_status || "No review"} />
              </TableCell>
              <TableCell className="font-normal text-black text-sm leading-[1.4] tracking-normal">
                {formatDate(app.updated_at)}
              </TableCell>
              <TableCell className="font-normal text-black text-sm leading-[1.4] tracking-normal">
                <div className="flex items-center gap-2">
                  <Avatar className="h-6 w-6">
                    <AvatarFallback>{app.updated_by.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <span>{app.updated_by}</span>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
