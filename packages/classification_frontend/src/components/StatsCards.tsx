"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";

interface StatCardData {
  title: string;
  value: string;
}

const statsData: StatCardData[] = [
  {
    title: "Total Applications",
    value: "1,045",
  },
  {
    title: "Approved",
    value: "934",
  },
  {
    title: "Rejected",
    value: "183",
  },
  {
    title: "Flagged for Review",
    value: "128",
  },
];

export function StatsCards() {
  return (
    <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {statsData.map((stat, index) => (
        <Card
          className="h-auto w-auto rounded-[6px] border border-[#E5E5E5] bg-white shadow-sm"
          key={index}
        >
          <CardHeader className="pb-2">
            <h3 className="font-medium text-[#0A0A0A] text-sm">{stat.title}</h3>
          </CardHeader>
          <CardContent className="flex h-full flex-col justify-between pt-0">
            <div className="mt-6 flex items-start justify-between gap-4">
              <div className="flex flex-col items-start justify-start gap-2">
                <div className="flex items-center justify-start gap-1">
                  <span className="font-medium text-3xl">{stat.value}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
