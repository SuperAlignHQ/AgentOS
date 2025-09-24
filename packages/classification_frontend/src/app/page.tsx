"use client";

import { Scale } from "lucide-react";
import { useState } from "react";
import { CreateApplicationSheet } from "@/components/createApplicationSheet";
import { Header } from "@/components/Header";
import { PageHeader } from "@/components/PageHeader";
import { AppSidebar } from "@/components/Sidebar";
import { TabsFilters } from "@/components/TabsFilters";

export default function UnderwritingDashboard() {
  const [isCreateSheetOpen, setIsCreateSheetOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState("overview");

  return (
    <>
      <AppSidebar />

      {/* Main content */}
      <main className="flex flex-1 flex-col overflow-hidden">
        <PageHeader
          data={{
            icon: Scale,
            heading: "Underwriting",
            domain: "underwriting",
          }}
        />
        <Header
          onNewApplicationClick={() => setIsCreateSheetOpen(true)}
          selectedTab={selectedTab}
        />

        {/* Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            <TabsFilters
              onTabChange={setSelectedTab}
              onCreateApplication={() => setIsCreateSheetOpen(true)}
              selectedTab={selectedTab}
            />
          </div>
        </div>
      </main>

      <CreateApplicationSheet
        isOpen={isCreateSheetOpen}
        onClose={() => setIsCreateSheetOpen(false)}
      />
    </>
  );
}
