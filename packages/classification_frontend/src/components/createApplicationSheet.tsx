"use client";

import { Upload } from "lucide-react";
import { useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { toast } from "sonner";
import { createApplication } from "@/server/server";



interface CreateApplicationSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CreateApplicationSheet({
  isOpen,
  onClose,
}: CreateApplicationSheetProps) {
  const [applicationId, setApplicationId] = useState("");
  const [applicationType, setApplicationType] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: async () => {
      return await createApplication(
        "2f0ceb85-f099-4223-b6c8-cd5465dfd185",
        "1a5eb87f-a8b1-47f9-8ff7-59749114c045",
        {
          application_type: applicationType,
          application_id: applicationId,
          reason_code: "D2",
        },
        selectedFiles
      );
    },
    onMutate: () => {
      toast.success("Creating application...", {
        description: "Please wait while we create the application.",
        duration: 4000,
      });
    },
    onSuccess: () => {
      toast.success("Application created successfully!", {
        description:
          "The application has been created and will appear in the application list.",
        duration: 4000,
      });
      // Refresh applications list
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      // Reset form
      setApplicationId("");
      setApplicationType("");
      setSelectedFiles([]);
      // Optionally close sheet
      // onClose();
    },
    onError: (error) => {
      if (error instanceof Error) {
        if (error.message.includes("timeout")) {
          toast.error("Request timeout", {
            description: "The server took too long to process your files. Please try again.",
            duration: 5000,
          });
          return;
        }
        if (error.message.includes("504")) {
          toast.error("Server timeout", {
            description: "The server is temporarily unavailable. Please try again in a moment.",
            duration: 5000,
          });
          return;
        }
        if (error.message.includes("404")) {
          toast.error("Service not found", {
            description: "The application creation service is currently unavailable.",
            duration: 5000,
          });
          return;
        }
        toast.error("Failed to create application", {
          description: error.message || "Please try again later.",
          duration: 5000,
        });
      } else {
        toast.error("Failed to create application", {
          description: "An unexpected error occurred. Please try again.",
          duration: 5000,
        });
      }
    },
  });

  const handleFileSelect = (files: FileList | null) => {
    if (files) {
      const fileArray = Array.from(files);
      setSelectedFiles((prev) => [...prev, ...fileArray]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleFileInputClick = () => {
    fileInputRef.current?.click();
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (!applicationId || !applicationType || selectedFiles.length === 0) {
      toast.warning("Please fill in all required fields", {
        description:
          "Application ID, Application Type, and at least one document are required.",
        duration: 3000,
      });
      return;
    }

    // Close the sheet immediately
    onClose();

    // Start the mutation in the background
    await create.mutateAsync();
  };

  // Handle sheet close
  const handleClose = () => {
    // Reset mutation state when closing
    create.reset();
    onClose();
  };

  return (
    <Sheet onOpenChange={handleClose} open={isOpen}>
      <SheetContent className="w-full max-w-full p-0">
        <div className="flex h-full flex-col">
          <SheetHeader className="border-b px-6 py-4">
            <SheetTitle className="font-semibold text-xl leading-tight tracking-tight">
              Create an Application
            </SheetTitle>
          </SheetHeader>

          <div className="flex-1 overflow-auto px-6 py-6">
            <div className="space-y-6">
              <div className="space-y-2">
                <Label className="font-medium text-sm" htmlFor="application-id">
                  Application ID
                </Label>
                <Input
                  className="text-sm"
                  id="application-id"
                  onChange={(e) => setApplicationId(e.target.value)}
                  value={applicationId}
                />
              </div>

              <div className="space-y-2">
                <Label
                  className="font-medium text-sm"
                  htmlFor="application-type"
                >
                  Application Type
                </Label>

                <Input
                  className="text-sm"
                  id="application-type"
                  onChange={(e) => setApplicationType(e.target.value)}
                  value={applicationType}
                />
              </div>

              <div className="space-y-2">
                <Label className="font-medium text-sm">Documents</Label>
                <div
                  className={`rounded-lg border-2 border-dashed p-8 text-center transition-colors ${isDragOver
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50"
                    }`}
                  onClick={handleFileInputClick}
                  onDragLeave={handleDragLeave}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                >
                  <div className="flex flex-col items-center gap-4">
                    <Upload className="h-12 w-12 text-muted-foreground" />
                    <div>
                      <p className="text-muted-foreground text-sm leading-relaxed">
                        Drag & drop files here, or click to select
                      </p>
                      <p className="mt-1 text-muted-foreground text-xs">
                        Supports multiple files
                      </p>
                      <Button
                        className="mt-4"
                        type="button"
                        variant="secondary"
                      >
                        Choose files
                      </Button>
                    </div>
                  </div>
                  <input
                    className="hidden"
                    multiple
                    onChange={(e) => handleFileSelect(e.target.files)}
                    ref={fileInputRef}
                    type="file"
                  />
                </div>

                {selectedFiles.length > 0 && (
                  <div className="space-y-2">
                    <Label className="font-medium text-sm">
                      Selected files:
                    </Label>
                    <div className="space-y-1">
                      {selectedFiles.map((file, index) => (
                        <div
                          className="flex items-center justify-between rounded-md bg-muted p-2"
                          key={index}
                        >
                          <span className="mr-2 flex-1 truncate text-sm">
                            {file.name}
                          </span>
                          <Button
                            onClick={() => removeFile(index)}
                            size="sm"
                            variant="ghost"
                          >
                            ×
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="border-t px-6 py-4">
            <div className="flex justify-end gap-3">
              <Button
                onClick={handleClose}
                variant="outline"
              >
                Cancel
              </Button>
              <Button
                disabled={selectedFiles.length === 0}
                onClick={handleSubmit}
              >
                Create Application
              </Button>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
