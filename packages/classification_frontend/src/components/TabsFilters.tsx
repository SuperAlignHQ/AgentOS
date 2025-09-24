"use client";

import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
  MoveLeft,
  MoveRight,
  PencilIcon,
  Search,
} from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import type { Application } from "@/components/ApplicationsTable";
import { ApplicationsTable } from "@/components/ApplicationsTable";
import { ApprovalDialog } from "@/components/ApprovalDialog";
import { StatsCards } from "@/components/StatsCards";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  findApplicationInList,
  useApplications,
} from "@/hooks/useApplications";
import { APPROVED, capitalizeFirstLetter, FAIL, formatText, NEW, PASS, SUSPENDED } from "@/lib/utils";
import { updateUnderwriterStatus } from "@/server/server";
import { Textarea } from "./ui/textarea";
import dynamic from "next/dynamic";

const DocumentEvaluationDrawer = dynamic(
  () => import("@/components/DocumentEvaluationDrawer").then((m) => m.DocumentEvaluationDrawer),
  { ssr: false }
);

interface TabsFiltersProps {
  selectedTab: string;
  onTabChange: (tab: string) => void;
  onCreateApplication?: () => void;
}

export function TabsFilters({ selectedTab, onTabChange, onCreateApplication }: TabsFiltersProps) {
  const [currentApplicationIndex, setCurrentApplicationIndex] = useState(0);
  const [selectedApplicationId, setSelectedApplicationId] = useState<string>("");
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [declineDialogOpen, setDeclineDialogOpen] = useState(false);
  const [suspendDialogOpen, setSuspendDialogOpen] = useState(false);
  const [documentEvaluationOpen, setDocumentEvaluationOpen] = useState(false);

  const {
    data: applicationsData,
    isLoading: applicationsLoading,
    refetch,
  } = useApplications();

  const applications = applicationsData?.applications || [];
  const selectedApplication = selectedApplicationId
    ? findApplicationInList(applications, selectedApplicationId)
    : undefined;

  // Set the first application as selected when data is loaded
  useEffect(() => {
    if (applications.length > 0 && !selectedApplicationId) {
      setSelectedApplicationId(applications[0].application_id);
      setCurrentApplicationIndex(0);
    }
  }, [applications, selectedApplicationId]);

  // Remove the conflicting useEffect that was causing sync issues
  // Keep currentApplicationIndex in sync with selectedApplicationId - REMOVED

  const handleApplicationClick = (application: Application) => {
    const applicationIndex = applications.findIndex(
      (app) => app.application_id === application.application_id
    );

    if (applicationIndex !== -1) {
      setSelectedApplicationId(application.application_id);
      setCurrentApplicationIndex(applicationIndex);
      onTabChange("summary");
    }
  };

  const handleNextApplication = () => {
    if (currentApplicationIndex < applications.length - 1) {
      const nextIndex = currentApplicationIndex + 1;
      setCurrentApplicationIndex(nextIndex);
      setSelectedApplicationId(applications[nextIndex].application_id);
    }
  };

  const handlePreviousApplication = () => {
    if (currentApplicationIndex > 0) {
      const prevIndex = currentApplicationIndex - 1;
      setCurrentApplicationIndex(prevIndex);
      setSelectedApplicationId(applications[prevIndex].application_id);
    }
  };

  const handleBackToOverview = () => {
    onTabChange("overview");
    setSelectedApplicationId("");
    setCurrentApplicationIndex(0);
  };

  const handleOpenDocumentEvaluation = () => {
    setDocumentEvaluationOpen(true);
  };

  const handleApprove = async (notes: string) => {
    if (!selectedApplication) return;

    try {
      await updateUnderwriterStatus(
        selectedApplication.application_id,
        "approved",
        notes
      );
      toast.success("Application approved successfully");
      await refetch(); // Refresh the data
      setApproveDialogOpen(false);
    } catch (error) {
      if (error instanceof Error) {
        if (error.message.includes("timeout")) {
          toast.error("Request timeout", {
            description: "The server took too long to respond. Please try again.",
            duration: 5000,
          });
        } else if (error.message.includes("504")) {
          toast.error("Server timeout", {
            description: "The server is temporarily unavailable. Please try again in a moment.",
            duration: 5000,
          });
        } else {
          toast.error("Failed to approve application", {
            description: error.message,
            duration: 5000,
          });
        }
      } else {
        toast.error("Failed to approve application");
      }
      console.error("Error approving application:", error);
      throw error; // Re-throw to let dialog handle loading state
    }
  };

  const handleDecline = async (notes: string) => {
    if (!selectedApplication) return;

    try {
      await updateUnderwriterStatus(
        selectedApplication.application_id,
        "declined",
        notes
      );
      toast.success("Application declined successfully");
      await refetch(); // Refresh the data
      setDeclineDialogOpen(false);
    } catch (error) {
      if (error instanceof Error) {
        if (error.message.includes("timeout")) {
          toast.error("Request timeout", {
            description: "The server took too long to respond. Please try again.",
            duration: 5000,
          });
        } else if (error.message.includes("504")) {
          toast.error("Server timeout", {
            description: "The server is temporarily unavailable. Please try again in a moment.",
            duration: 5000,
          });
        } else {
          toast.error("Failed to decline application", {
            description: error.message,
            duration: 5000,
          });
        }
      } else {
        toast.error("Failed to decline application");
      }
      console.error("Error declining application:", error);
      throw error; // Re-throw to let dialog handle loading state
    }
  };

  const handleSuspend = async (notes: string) => {
    if (!selectedApplication) return;

    try {
      await updateUnderwriterStatus(
        selectedApplication.application_id,
        "suspended",
        notes
      );
      toast.success("Application suspended successfully");
      await refetch(); // Refresh the data
      setSuspendDialogOpen(false);
    } catch (error) {
      if (error instanceof Error) {
        if (error.message.includes("timeout")) {
          toast.error("Request timeout", {
            description: "The server took too long to respond. Please try again.",
            duration: 5000,
          });
        } else if (error.message.includes("504")) {
          toast.error("Server timeout", {
            description: "The server is temporarily unavailable. Please try again in a moment.",
            duration: 5000,
          });
        } else {
          toast.error("Failed to suspend application", {
            description: error.message,
            duration: 5000,
          });
        }
      } else {
        toast.error("Failed to suspend application");
      }
      console.error("Error suspending application:", error);
      throw error;
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check if we're in the summary tab and have an application selected
      if (selectedTab !== "summary" || !selectedApplication) {
        return;
      }

      const isMac = navigator.platform.toUpperCase().indexOf("MAC") >= 0;
      const cmdKey = isMac ? event.metaKey : event.ctrlKey;

      if (cmdKey && !event.shiftKey && !event.altKey) {
        switch (event.key) {
          case "1":
            event.preventDefault();
            setApproveDialogOpen(true);
            break;
          case "2":
            event.preventDefault();
            setDeclineDialogOpen(true);
            break;
          case "3":
            event.preventDefault();
            setSuspendDialogOpen(true);
            break;
        }
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [selectedTab, selectedApplication]);

  // Reset selection when switching to overview
  useEffect(() => {
    if (selectedTab === "overview") {
      setSelectedApplicationId("");
      setCurrentApplicationIndex(0);
    }
  }, [selectedTab]);

  // Handle case when applications list changes (e.g., after refetch)
  useEffect(() => {
    if (selectedApplicationId && applications.length > 0) {
      const currentApp = findApplicationInList(applications, selectedApplicationId);
      if (!currentApp) {
        // Selected application no longer exists, reset to first application
        setSelectedApplicationId(applications[0]?.application_id || "");
        setCurrentApplicationIndex(0);
      } else {
        // Update index if application still exists but position changed
        const newIndex = applications.findIndex(
          (app) => app.application_id === selectedApplicationId
        );
        if (newIndex !== -1 && newIndex !== currentApplicationIndex) {
          setCurrentApplicationIndex(newIndex);
        }
      }
    }
  }, [applications, selectedApplicationId, currentApplicationIndex]);



  // Show loading state when there's no data
  if (applicationsLoading && applications.length === 0) {
    return (
      <div className="mb-6">
        <div className="flex h-48 items-center justify-center">
          <Skeleton className="h-8 w-48" />
        </div>
      </div>
    );
  }



  return (
    <div className="mb-6">
      <Tabs className="w-full" onValueChange={onTabChange} value={selectedTab}>
        <div className="flex items-center justify-between">
          <TabsList className="grid w-fit grid-cols-2">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="summary" disabled={applications.length === 0}>Summary</TabsTrigger>
          </TabsList>

          {selectedTab === "overview" && (
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="-translate-y-1/2 absolute top-1/2 left-3 h-4 w-4 transform text-muted-foreground" />
                <Input
                  className="w-64 pl-10"
                  placeholder="Search applications..."
                />
              </div>
              <Select defaultValue="all-statuses">
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all-statuses">All statuses</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {selectedTab === "summary" && (
            <div className="flex items-center gap-2">
              <Button
                className="h-9 w-9 p-5"
                disabled={currentApplicationIndex === 0}
                onClick={handlePreviousApplication}
                size="icon"
                variant="outline"
              >
                <MoveLeft className="h-4 w-4" />
              </Button>
              <span className="min-w-12 text-center font-strong text-sm">
                {String(currentApplicationIndex + 1).padStart(2, "0")}/
                {applications.length.toString().padStart(2, "0")}
              </span>
              <Button
                className="h-9 w-9 p-5"
                disabled={currentApplicationIndex === applications.length - 1}
                onClick={handleNextApplication}
                size="icon"
                variant="outline"
              >
                <MoveRight className="h-4 w-4" />
              </Button>
              <Button
                className="gap-2 border border-[#E5E5E5] bg-white px-4 py-1 font-semibold text-sm"
                onClick={handleOpenDocumentEvaluation}
                size="lg"
                variant="outline"
              >
                Evaluate documents
              </Button>
            </div>
          )}
        </div>

        <TabsContent className="mt-4" value="overview">
          <div className="w-full space-y-6">
            {/* <StatsCards /> */}
            <ApplicationsTable
              onApplicationClick={handleApplicationClick}
              onCreateApplication={onCreateApplication}
            />
          </div>
        </TabsContent>

        <TabsContent className="mt-4" value="summary">
          {applicationsLoading ? (
            <div className="flex h-48 items-center justify-center">
              <Skeleton className="h-8 w-48" />
            </div>
          ) : selectedApplication ? (
            <div className="w-full space-y-6">
              {/* Summary Header with Navigation */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4" />
              </div>

              {/* Application Detail Content */}
              <div className="space-y-6">
                {/* Action Buttons Row */}
                <div className="mx-6 flex items-center justify-between gap-1">
                  <div className="flex items-center gap-1">
                    <h2
                      className="font-bold text-xl"
                      style={{
                        fontWeight: "bold",
                        lineHeight: "120%",
                        letterSpacing: "0%",
                      }}
                    >
                      {selectedApplication.application_id}
                    </h2>
                    <Button
                      className="h-9 w-9 p-5"
                      size="default"
                      variant="ghost"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      className="h-9 w-[119px] gap-1 rounded border border-[#E5E5E5] bg-[#F5F5F5] pt-1 pr-4 pb-1 pl-4 font-semibold text-sm leading-[1.4] tracking-normal"
                      onClick={() => setApproveDialogOpen(true)}
                      variant="outline"
                    >
                      Approve{" "}
                      <Badge className="ml-1" variant="secondary">
                        ⌘1
                      </Badge>
                    </Button>
                    <Button
                      className="h-9 w-[119px] gap-2 rounded border border-[#E5E5E5] bg-[#F5F5F5] pt-1 pr-4 pb-1 pl-4 font-semibold text-sm leading-[1.4] tracking-normal"
                      onClick={() => setDeclineDialogOpen(true)}
                      variant="outline"
                    >
                      Decline{" "}
                      <Badge className="ml-1" variant="secondary">
                        ⌘2
                      </Badge>
                    </Button>
                    <Button
                      className="h-9 w-[119px] gap-2 rounded border border-[#E5E5E5] bg-[#F5F5F5] pt-1 pr-4 pb-1 pl-4 font-semibold text-sm leading-[1.4] tracking-normal"
                      onClick={() => setSuspendDialogOpen(true)}
                      variant="outline"
                    >
                      Suspend{" "}
                      <Badge className="ml-2" variant="secondary">
                        ⌘3
                      </Badge>
                    </Button>
                  </div>
                </div>

                {/* Case Information Panel */}
                <div className="p-4">
                  <h3 className="mb-6 font-semibold text-lg">
                    Case Information Panel
                  </h3>

                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="font-medium text-sm leading-[1.4] tracking-normal">
                        Application Code:{" "}
                        <span className="font-normal">
                          {selectedApplication.application_type}
                        </span>
                      </div>

                      <div className="font-medium text-sm leading-[1.4] tracking-normal">
                        Application ID:{" "}
                        <span className="font-normal">
                          {selectedApplication.application_id}
                        </span>
                      </div>

                      <div className="font-medium text-sm leading-[1.4] tracking-normal">
                        Policy Check:{" "}
                        <span
                          className={`font-normal ${selectedApplication.policy_check === "pass" ? "text-green-600" : "text-red-600"}`}
                        >
                          {capitalizeFirstLetter(
                            selectedApplication.policy_check
                          )}
                        </span>
                      </div>

                      <div className="font-medium text-sm leading-[1.4] tracking-normal">
                        Document Check:{" "}
                        <span
                          className={`font-normal ${selectedApplication.overall_document_check_status === PASS ? "text-green-600" : "text-red-600"}`}
                        >
                          {capitalizeFirstLetter(
                            selectedApplication.overall_document_check_status
                          )}
                        </span>
                      </div>

                      <div className="font-medium text-sm leading-[1.4] tracking-normal">
                        System Status:{" "}
                        <span
                          className={`font-normal ${selectedApplication.system_status.toLowerCase() === APPROVED ? "text-green-600" : "text-red-600"}`}
                        >
                          {formatText(selectedApplication.system_status)}
                        </span>
                      </div>
                      <div className="font-medium text-sm leading-[1.4] tracking-normal">
                        Underwriter Status:{" "}

                        <span
                          className={`font-normal ${selectedApplication.underwriter_status.toLowerCase() === APPROVED ? "text-green-600" : (selectedApplication.underwriter_status.toLowerCase() === NEW || selectedApplication.underwriter_status.toLowerCase() === SUSPENDED ? "text-yellow-600" : "text-red-600")}`}
                        >
                          {formatText(selectedApplication.underwriter_status)}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="font-medium text-sm leading-[1.4] tracking-normal">
                        Underwriter Review:{" "}
                        <Textarea className="mt-1 block rounded bg-muted p-3 font-normal" readOnly value={selectedApplication.underwriter_review as string} />


                      </div>
                    </div>
                  </div>
                </div>

                {/* Document Check Table */}
                <div className="w-auto">
                  <div className="pl-6">
                    <p className="font-semibold text-lg">Document check</p>
                  </div>
                  <div className="p-4">
                    <Table className="gap-2 border border-b">
                      <TableHeader className="bg-[#F5F5F5]">
                        <TableRow className="h-[56px] w-[1392px] border-b">
                          <TableHead className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                            Document Category
                          </TableHead>
                          <TableHead className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                            Documents
                          </TableHead>
                          <TableHead className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                            Validation
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedApplication.document_result.map(
                          (item, index) => (
                            <TableRow
                              className={`h-[56px] w-[1392px] ${item.result ? "" : "bg-[#FEF3F2]"}`}
                              key={index}
                            >
                              <TableCell className="py-0 font-normal text-sm leading-[1.4] tracking-normal">
                                {formatText(item.document_category)}
                              </TableCell>
                              <TableCell className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                                {formatText(item.document_type)}
                              </TableCell>
                              <TableCell className="py-0">
                                <span
                                  className={`font-medium text-xs ${item.result ? "text-green-600" : "text-red-600"}`}
                                >
                                  {item.result ? "Pass" : "Fail"}
                                </span>
                              </TableCell>
                            </TableRow>
                          )
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </div>

                {/* Policy Check Table */}
                <div className="w-auto">
                  <div className="pl-6">
                    <h3 className="font-semibold text-lg">Policy check</h3>
                  </div>
                  <div className="p-4">
                    <Table className="gap-2 border border-b">
                      <TableHeader className="bg-[#F5F5F5]">
                        <TableRow className="h-[56px] w-[1392px] border-b">
                          <TableHead className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                            Policy Name
                          </TableHead>
                          <TableHead className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                            Documents
                          </TableHead>
                          <TableHead className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                            Validation
                          </TableHead>
                          <TableHead className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                            Result
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedApplication.policy_check_result.map(
                          (item, index) => (
                            <TableRow
                              className={`h-[56px] w-[1392px] border-b ${item.validation_result.toLowerCase() === FAIL ? "bg-[#FEF3F2]" : ""}`}
                              key={index}
                            >
                              <TableCell className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                                {formatText(item.policy_name)}
                              </TableCell>
                              <TableCell className="py-0 font-medium text-sm leading-[1.2] tracking-normal">
                                {formatText(item.doc_type)}
                              </TableCell>
                              <TableCell className="py-0 ">
                                <span
                                  className={`font-medium text-xs ${item.validation_result.toLowerCase() === PASS ? "text-green-600" : "text-red-600"}`}
                                >
                                  {item.validation_result.toLowerCase() === PASS ? "Pass" : "Fail"}
                                </span>
                              </TableCell>
                              <TableCell className="py-0 font-normal text-sm leading-[1.4] tracking-normal">
                                {item.comment || "N/A"}
                              </TableCell>
                            </TableRow>
                          )
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex h-48 items-center justify-center">
              <div className="text-center">
                <p className="text-muted-foreground">
                  Select an application from the Overview tab to view its
                  details.
                </p>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Dialogs */}
      <ApprovalDialog
        cancelText="Cancel"
        confirmText="Proceed to Approve"
        description="Are you sure you want to mark the application as approved?"
        isOpen={approveDialogOpen}
        onClose={() => setApproveDialogOpen(false)}
        onConfirm={handleApprove}
        title="Approve application"
      />

      <ApprovalDialog
        cancelText="Cancel"
        confirmText="Proceed to Decline"
        description="Are you sure you want to mark the application as declined?"
        isDestructive={true}
        isOpen={declineDialogOpen}
        onClose={() => setDeclineDialogOpen(false)}
        onConfirm={handleDecline}
        title="Decline application"
      />

      <ApprovalDialog
        cancelText="Cancel"
        confirmText="Proceed to Suspend"
        description="Are you sure you want to mark the application as suspended?"
        isDestructive={true}
        isOpen={suspendDialogOpen}
        onClose={() => setSuspendDialogOpen(false)}
        onConfirm={handleSuspend}
        title="Suspend application"
      />

      <DocumentEvaluationDrawer
        isOpen={documentEvaluationOpen}
        onClose={() => setDocumentEvaluationOpen(false)}
        documents={selectedApplication?.documents || []}
        applicationId={selectedApplication?.application_id || ""}
      />
      {/* Add padding at bottom to prevent overlap with drawer */}
      <div className="h-4" />
    </div>
  );
}