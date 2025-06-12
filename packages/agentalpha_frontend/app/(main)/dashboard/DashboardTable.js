"use client"

import * as React from "react"
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { ArrowUpDown, MoreHorizontal, PlusIcon, Search as SearchIcon } from "lucide-react"
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
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

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
    cell: ({ row }) => <div className="ml-4">{row.getValue("applicationId")}</div>,
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
            <DropdownMenuItem>View details</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]

export function DashboardTable() {
  const [sorting, setSorting] = React.useState([])
  const [columnFilters, setColumnFilters] = React.useState([])
  const [columnVisibility, setColumnVisibility] = React.useState({})
  const [rowSelection, setRowSelection] = React.useState({})

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  })

  return (
    <div className="w-full mt-2">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold"> Today's Applications</h2>
        <MoreVertIcon />
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
