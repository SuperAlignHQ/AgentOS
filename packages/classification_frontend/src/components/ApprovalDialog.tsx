"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface ApprovalDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (notes: string) => void;
  title: string;
  description: string;
  confirmText: string;
  cancelText: string;
  isDestructive?: boolean;
}

export function ApprovalDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText,
  cancelText,
  isDestructive = false,
}: ApprovalDialogProps) {
  const [notes, setNotes] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleConfirm = async () => {
    setIsLoading(true);
    try {
      await onConfirm(notes);
      setNotes("");
      onClose();
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setNotes("");
    onClose();
  };

  return (
    <Dialog onOpenChange={handleClose} open={isOpen}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="font-bold text-black text-sm leading-[1.4] tracking-normal">
            {title}
          </DialogTitle>
          <DialogDescription className="font-normal text-black text-xs leading-[1.4] tracking-normal">
            {description}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="notes">
              Add notes <span className="text-red-500">*</span>
            </Label>
            <Input
              className="w-full"
              id="notes"
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes"
              value={notes}
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            disabled={isLoading}
            onClick={handleClose}
            type="button"
            variant="outline"
          >
            {cancelText}
          </Button>
          <Button
            disabled={isLoading || !notes.trim()}
            onClick={handleConfirm}
            type="button"
            variant={isDestructive ? "destructive" : "default"}
          >
            {isLoading ? "Processing..." : confirmText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
