"use client"

import * as React from "react"
import { ArrowUpDown } from "lucide-react"
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DataTable } from "@/components/DataTable";     

const policiesData = [
    {
      policyId: "PL-96634",
      policyName: "Document Consistency",
      documentType: ["P60"],
      policyPhase: "Testing",
    },
    {
      policyId: "PL-99154",
      policyName: "Payslip YTD Check",
      documentType: ["P60", "Passport"],
      policyPhase: "Production",
    },
    {
      policyId: "PL-90542",
      policyName: "Overall Validation",
      documentType: ["P60"],
      policyPhase: "Testing",
    },
    {
      policyId: "PL-57577",
      policyName: "Undated Payslips",
      documentType: ["P60"],
      policyPhase: "Production",
    },
    {
      policyId: "PL-21129",
      policyName: "Document Consistency",
      documentType: ["Payslip", "P60"],
      policyPhase: "Testing",
    },
    {
      policyId: "PL-12618",
      policyName: "Payslip YTD Check",
      documentType: ["P60"],
      policyPhase: "Production",
    },
    {
      policyId: "PL-18631",
      policyName: "Overall Validation",
      documentType: ["P60"],
      policyPhase: "Testing",
    },
    {
      policyId: "PL-55096",
      policyName: "Undated Payslips",
      documentType: ["Bank Statement", "P60"],
      policyPhase: "Production",
    },
    {
      policyId: "PL-32635",
      policyName: "Document Consistency",
      documentType: ["P60"],
      policyPhase: "Testing",
    },
];

const TagBadge = ({ tags }) => {
    return (
        <div className="flex flex-wrap gap-2">
            {tags.map(tag => (
                <span key={tag} className="bg-gray-100 text-gray-800 px-2.5 py-1 text-xs font-semibold rounded-full w-max">
                    {tag}
                </span>
            ))}
        </div>
    )
}

const PhaseBadge = ({ phase }) => {
    const baseClasses = "px-2.5 py-1 text-xs font-semibold rounded-full w-max";
    const phaseClasses = {
      "Testing": "bg-blue-100 text-blue-800",
      "Production": "bg-green-100 text-green-800",
    };
    return (
      <div className="flex">
        <span className={`${baseClasses} ${phaseClasses[phase] || "bg-gray-100 text-gray-800"}`}>
        {phase}
        </span>
      </div>
    );
}

export const policiesColumns = [
    {
        accessorKey: "policyId",
        header: ({ column }) => (
            <Button
                variant="ghost"
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
                Policy ID
                <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
        ),
        cell: ({ row }) => <div className="ml-4">{row.getValue("policyId")}</div>,
    },
    {
        accessorKey: "policyName",
        header: ({ column }) => (
            <Button
                variant="ghost"
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
                Policy Name
                <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
        ),
        cell: ({ row }) => <div className="ml-4 capitalize">{row.getValue("policyName")}</div>,
    },
    {
        accessorKey: "documentType",
        header: "Document Type",
        cell: ({ row }) => <TagBadge tags={row.getValue("documentType")} />,
        filterFn: (row, columnId, filterValue) => {
            if (!filterValue) return true;
            const value = row.getValue(columnId);
            return value.includes(filterValue);
        }
    },
    {
        accessorKey: "policyPhase",
        header: "Policy Phase",
        cell: ({ row }) => <PhaseBadge phase={row.getValue("policyPhase")} />
    },
    {
        id: "actions",
        enableHiding: false,
        cell: ({ row }) => {
            const policy = row.original;
            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Open menu</span>
                            <MoreVertIcon className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuItem
                            onClick={() => navigator.clipboard.writeText(policy.policyId)}
                        >
                            Copy policy ID
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>View details</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
];

const documentTypeFilterOptions = [
    { value: 'P60', label: 'P60' },
    { value: 'Passport', label: 'Passport' },
    { value: 'Payslip', label: 'Payslip' },
    { value: 'Bank Statement', label: 'Bank Statement' },
]

export function PoliciesTable({ onNewPolicyClick }) {
    return (
        <DataTable
            title="Policies"
            data={policiesData}
            columns={policiesColumns}
            searchKey="policyName"
            searchPlaceholder="Search by Policy Name..."
            filterColumn="documentType"
            filterOptions={documentTypeFilterOptions}
            filterPlaceholder="All Documents"
            onNewClick={onNewPolicyClick}
            newButtonText="New Policy"
        />
    )
} 