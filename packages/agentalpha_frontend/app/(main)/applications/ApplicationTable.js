"use client"

import * as React from "react"
import Link from "next/link";
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
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { DataTable } from "@/components/DataTable";

const data = [
    {
      applicationId: "LN-02394456",
      date: "13 Apr",
      status: "Pending Approval",
      assignedTo: { name: "Cynthia Luettgen" },
    },
    {
      applicationId: "LN-02629410",
      date: "13 Apr",
      status: "Pending Approval",
      assignedTo: { name: "Dale Hills" },
    },
    {
      applicationId: "LN-18302410",
      date: "13 Apr",
      status: "Flagged",
      assignedTo: { name: "Lynette Nienow" },
    },
    {
      applicationId: "LN-53480512",
      date: "13 Apr",
      status: "Flagged",
      assignedTo: { name: "Lillian Streich" },
    },
    {
      applicationId: "LN-8092071412",
      date: "12 Apr",
      status: "Pending Approval",
      assignedTo: { name: "Nora Wyman" },
    },
    {
      applicationId: "LN-02412645",
      date: "12 Apr",
      status: "Pending Approval",
      assignedTo: { name: "Lynn Gleichner" },
    },
    {
      applicationId: "LN-35102412",
      date: "12 Apr",
      status: "Rejected",
      assignedTo: { name: "Ron Abshire" },
    },
    {
      applicationId: "LN-89602167",
      date: "11 Apr",
      status: "Pending Approval",
      assignedTo: { name: "Joey Tremblay" },
    },
    {
      applicationId: "LN-61852167",
      date: "11 Apr",
      status: "Approved",
      assignedTo: { name: "Seth Fadel" },
    },
  ];

const StatusBadge = ({ status }) => {
    const baseClasses = "px-2.5 py-1 text-xs font-semibold rounded-full w-max";
    const statusClasses = {
      "Pending Approval": "bg-gray-100 text-gray-800",
      "Flagged": "bg-yellow-100 text-yellow-800",
      "Rejected": "bg-red-100 text-red-800",
      "Approved": "bg-green-100 text-green-800",
    };
    return (
      <div className="flex">
        <span className={`${baseClasses} ${statusClasses[status] || "bg-gray-100 text-gray-800"}`}>
        {status}
        </span>
      </div>
    );
  };

export const columns = [
  {
    accessorKey: "applicationId",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Application ID
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => (
        <Link href={`/applications/${row.getValue("applicationId")}`} className="ml-4 ">
            {row.getValue("applicationId")}
        </Link>
    ),
  },
  {
    accessorKey: "date",
    header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Date
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
    cell: ({ row }) => <div className="ml-4">{row.getValue("date")}</div>,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => <StatusBadge status={row.getValue("status")} />,
  },
  {
    accessorKey: "assignedTo",
    header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Assigned to
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
    },
    cell: ({ row }) => {
        const assignedTo = row.getValue("assignedTo");
        return (
          <div className="flex items-center space-x-2 ml-4">
            <AccountCircleIcon className="h-6 w-6 text-gray-400" />
            <span>{assignedTo.name}</span>
          </div>
        );
    },
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const application = row.original

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
              onClick={() => navigator.clipboard.writeText(application.applicationId)}
            >
              Copy application ID
            </DropdownMenuItem>
            <DropdownMenuSeparator />
              <DropdownMenuItem>
              <Link href={`/applications/${application.applicationId}`}>View details</Link>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]

const statusFilterOptions = [
    { value: 'Pending Approval', label: 'Pending Approval'},
    { value: 'Flagged', label: 'Flagged'},
    { value: 'Approved', label: 'Approved'},
    { value: 'Rejected', label: 'Rejected'},
]

export function ApplicationTable({ onNewApplicationClick }) {
  return (
      <DataTable
        title="Applications"
        data={data}
        Link={Link}
        columns={columns}
        searchKey="applicationId"
        searchPlaceholder="Search by Application ID..."
        filterColumn="status"
        filterOptions={statusFilterOptions}
        filterPlaceholder="All Status"
        onNewClick={onNewApplicationClick}
        newButtonText="New Application"
    />
  )
}
