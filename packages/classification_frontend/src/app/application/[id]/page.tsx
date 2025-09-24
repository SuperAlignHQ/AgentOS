"use client";

import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// Mock data for document check
const documentCheckData = [
  {
    category: "Income",
    documents: "Contract of employment",
    validation: "Fail",
    result:
      "P60 is older than 12 months. Minimum 3 months of Payslips required.",
    isFail: true,
  },
  {
    category: "Expenditure",
    documents: "Bank statement",
    validation: "Pass",
    result: "All required documents are present",
    isFail: false,
  },
  {
    category: "ID Proof",
    documents: "Marriage certificate",
    validation: "Pass",
    result: "All required documents are present",
    isFail: false,
  },
];

// Mock data for policy check
const policyCheckData = [
  {
    reasonCode: "OMR-20250724-1234",
    policyName: "Remortgage",
    documents: "Contract of employment",
    validation: "Fail",
    review:
      "P60 is older than 12 months. Minimum 3 months of Payslips required.",
    isFail: true,
  },
  {
    reasonCode: "OMR-20250724-1235",
    policyName: "Remortgage",
    documents: "Bank statement",
    validation: "Pass",
    review: "All required documents are present",
    isFail: false,
  },
];

interface ApplicationDetailPageProps {
  params: {
    id: string;
  };
}

export default function ApplicationDetailPage({
  params,
}: ApplicationDetailPageProps) {
  const router = useRouter();

  // Convert application ID to start from 1
  const applicationNumber = Number.parseInt(params.id) + 1;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-white">
        <div className="flex items-center gap-4 px-6 py-4">
          <Button
            className="h-8 w-8 p-0"
            onClick={() => router.back()}
            size="sm"
            variant="ghost"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="flex items-center gap-2">
            <h1
              className="font-bold text-xl"
              style={{
                fontWeight: "bold",
                lineHeight: "120%",
                letterSpacing: "0%",
              }}
            >
              B023944563
            </h1>
            <Badge className="text-xs" variant="outline">
              {applicationNumber}
            </Badge>
          </div>
        </div>
      </div>

      <div className="space-y-8 p-6">
        {/* Case Information Panel */}
        <div className="rounded-lg border bg-card p-6">
          <h2 className="mb-6 font-semibold text-lg">Case Information Panel</h2>

          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <div className="mb-1 font-medium text-sm leading-[1.4] tracking-normal">
                  Decision
                </div>
                <div className="font-normal text-sm leading-[1.4] tracking-normal">
                  Approved - Underwritten by RCS
                </div>
              </div>

              <div>
                <div className="mb-1 font-medium text-sm leading-[1.4] tracking-normal">
                  Application ID
                </div>
                <div className="font-normal text-sm leading-[1.4] tracking-normal">
                  B023944563
                </div>
              </div>

              <div>
                <div className="mb-1 font-medium text-sm leading-[1.4] tracking-normal">
                  Policy Check
                </div>
                <div className="font-normal text-sm leading-[1.4] tracking-normal">
                  Pass
                </div>
              </div>

              <div>
                <div className="mb-1 font-medium text-sm leading-[1.4] tracking-normal">
                  Document Check
                </div>
                <div className="font-normal text-sm leading-[1.4] tracking-normal">
                  Pass
                </div>
              </div>

              <div>
                <div className="mb-1 font-medium text-sm leading-[1.4] tracking-normal">
                  Fraud Check
                </div>
                <div className="font-normal text-sm leading-[1.4] tracking-normal">
                  Pass
                </div>
              </div>

              <div>
                <div className="mb-1 font-medium text-sm leading-[1.4] tracking-normal">
                  System Status
                </div>
                <div className="font-normal text-sm leading-[1.4] tracking-normal">
                  Pass
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="mb-1 font-medium text-sm leading-[1.4] tracking-normal">
                  Underwriter Review
                </div>
                <div className="rounded bg-muted p-3 font-normal text-sm leading-[1.4] tracking-normal">
                  All required documents are present.
                </div>
              </div>

              <div className="flex justify-end">
                <Button className="text-xs" variant="outline">
                  View more
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Document Check Table */}
        <div className="rounded-lg border bg-card">
          <div className="border-b p-6">
            <h2 className="font-semibold text-lg">Document check</h2>
          </div>
          <div className="p-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Document category
                  </TableHead>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Documents
                  </TableHead>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Validation
                  </TableHead>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Result
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documentCheckData.map((item, index) => (
                  <TableRow
                    className={item.isFail ? "bg-[#FEF3F2]" : ""}
                    key={index}
                  >
                    <TableCell className="font-normal text-sm leading-[1.4] tracking-normal">
                      {item.category}
                    </TableCell>
                    <TableCell className="font-medium text-sm leading-[1.2] tracking-normal">
                      {item.documents}
                    </TableCell>
                    <TableCell>
                      <Badge
                        className="font-medium text-xs"
                        variant={
                          item.validation === "Pass" ? "default" : "destructive"
                        }
                      >
                        {item.validation}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-normal text-sm leading-[1.4] tracking-normal">
                      {item.result}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Policy Check Table */}
        <div className="rounded-lg border bg-card">
          <div className="border-b p-6">
            <h2 className="font-semibold text-lg">Policy check</h2>
          </div>
          <div className="p-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Reason Code
                  </TableHead>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Policy Name
                  </TableHead>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Documents
                  </TableHead>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Validation
                  </TableHead>
                  <TableHead className="font-medium text-sm leading-[1.2] tracking-normal">
                    Underwriter Review
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {policyCheckData.map((item, index) => (
                  <TableRow
                    className={item.isFail ? "bg-[#FEF3F2]" : ""}
                    key={index}
                  >
                    <TableCell className="font-medium text-sm leading-[1.2] tracking-normal">
                      {item.reasonCode}
                    </TableCell>
                    <TableCell className="font-medium text-sm leading-[1.2] tracking-normal">
                      {item.policyName}
                    </TableCell>
                    <TableCell className="font-medium text-sm leading-[1.2] tracking-normal">
                      {item.documents}
                    </TableCell>
                    <TableCell>
                      <Badge
                        className="font-medium text-xs"
                        variant={
                          item.validation === "Pass" ? "default" : "destructive"
                        }
                      >
                        {item.validation}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-normal text-sm leading-[1.4] tracking-normal">
                      {item.review}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </div>
  );
}
