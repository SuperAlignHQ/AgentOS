import Sidebar from "@/components/Sidebar";
import Image from "next/image";
import { redirect } from "next/navigation";
import {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import Link from "next/link";
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
export default function Home() {
  return (
    <div>
    <div className="flex p-5 border-b justify-between items-center">
    <div>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>  
            <BreadcrumbPage>Home</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
    </div>
    <div className="flex items-center space-x-2">
      <AccountCircleIcon />
      <p>John Doe</p>
    </div>
    </div>
    </div>
  );
}
