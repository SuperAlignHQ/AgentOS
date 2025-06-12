'use client'
import React, {useState, useEffect} from 'react'
import Link from "next/link"
import {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import Card from '@/components/Card';
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import MoreVertIcon from '@mui/icons-material/MoreVert';
import {
    ChartConfig,
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
  } from "@/components/ui/chart"
  import { ApplicationTable, DataTableDemo } from '../applications/ApplicationTable';
import NewApplicationOverlay from '../applications/NewApplicationOverlay'
import { DashboardTable } from './DashboardTable';

const chartData = [
  { month: "January", desktop: 186 },
  { month: "February", desktop: 305 },
  { month: "March", desktop: 237 },
  { month: "April", desktop: 73 },
  { month: "May", desktop: 209 },
  { month: "June", desktop: 214},
]
const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-1))",
  },
}

const validationSuccessData = [
  { name: "P60", success: 72 },
  { name: "Payslip", success: 68 },
  { name: "Bank Statement", success: 82 },
  { name: "Passport", success: 75 },
];

const validationChartConfig = {
  success: {
    label: "Success",
    color: "hsl(var(--chart-1))",
  },
};

const page = () => {
  const [isOverlayVisible, setOverlayVisible] = useState(false);

  useEffect(() => {
    if (isOverlayVisible) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOverlayVisible]);

  return (
    <div className='flex flex-col bg-gray-50 overflow-hidden'>
    <div className='flex p-5 border-b  justify-between items-center'>
    <div>
      <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink asChild>
            <Link href="/">Home</Link>
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>    
        <BreadcrumbPage>Dashboard</BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
    </div>
     <div className="flex items-center space-x-2">
      <AccountCircleIcon />
      <p>John Doe</p>
      </div>
    </div>
    <div className='flex flex-col pl-5'>
    <h1 className='text-2xl mt-6'>Dashboard</h1>
     <div className='flex mt-4 space-x-5'>
      <Card title="Total Applications" value={1045} percentage={2.5} />
      <Card title="Approved" value={934} percentage={-1.2} />
      <Card title="Rejected" value={183} percentage={11} />
      <Card title="Flagged for Review" value={128} percentage={5.2} />
     </div> 

     <div className='flex space-x-5'>

       <div className='mt-4 w-1/2 flex flex-col justify-center border rounded-lg bg-white'>
       <div className='flex justify-between items-center p-4'>
       <div className='text-xl font-semibold'>Application Volume Over time</div>
        <div><MoreVertIcon /></div>
       </div>
       <div className='flex justify-center mt-6 items-center'>
       <ChartContainer config={chartConfig} className="w-full">
      <BarChart accessibilityLayer data={chartData}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="month"
          tickLine={false}
          tickMargin={10}
          axisLine={false}
          tickFormatter={(value) => value.slice(0,9)}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          allowDecimals={false}
          tickCount={8}
        />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} barSize={40} />
      </BarChart>
    </ChartContainer>
    </div>
       </div> 

       <div className='mt-4 w-1/2 flex flex-col justify-center border rounded-lg bg-white'>
        <div className='flex justify-between items-center p-4'>
            <div className='text-xl font-semibold'>Validation Success Rate</div>
            <div><MoreVertIcon /></div>
        </div>
        <div className='flex justify-center items-center p-4'>
            <ChartContainer config={validationChartConfig} className="w-full">
                <BarChart
                    accessibilityLayer
                    data={validationSuccessData}
                    layout="vertical"
                    margin={{
                        left: 10,
                    }}
                >
                    <CartesianGrid horizontal={false} />
                    <YAxis
                        dataKey="name"
                        type="category"
                        tickLine={false}
                        tickMargin={10}
                        axisLine={false}
                        width={100}
                       
                    />
                    <XAxis dataKey="success" type="number" domain={[0, 100]} tickFormatter={(value) => `${value}%`}  tickCount={6} />
                    <ChartTooltip
                        cursor={false}
                        content={<ChartTooltipContent indicator="line" />}
                    />
                    <Bar
                        dataKey="success"
                        layout="vertical"
                        fill="var(--color-success)"
                        radius={4}
                        barSize={40}
                    />
                </BarChart>
            </ChartContainer>
        </div>
    </div>

       </div>

       <div className='border rounded-lg mt-4 p-4 bg-white'>
       <DashboardTable />
       </div>
    </div>
    </div>
  )
}

export default page
