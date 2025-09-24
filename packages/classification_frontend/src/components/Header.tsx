"use client";

import { Button } from "@/components/ui/button";

interface HeaderProps {
  onNewApplicationClick: () => void;
  selectedTab: string;
}

export function Header({ onNewApplicationClick, selectedTab }: HeaderProps) {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-semibold text-2xl leading-tight tracking-tight">
            Underwriting
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed">
            All your loan applications, organized and up to date—at a glance.
          </p>
        </div>
        {selectedTab === "overview" && (
          <Button
            className="bg-primary text-primary-foreground"
            onClick={onNewApplicationClick}
          >
            <svg
              className="mr-2 h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M12 4v16m8-8H4"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
              />
            </svg>
            New application
          </Button>
        )}
      </div>
    </div>
  );
}
