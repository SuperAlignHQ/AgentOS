"use client"

import React, { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';     
import { PoliciesTable } from './PoliciesTable';
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import Link from 'next/link'
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import NewPolicyOverlay from './NewPolicyOverlay';

export default function Policies() {
  const [isOverlayVisible, setOverlayVisible] = useState(false);

  const handleNewPolicyClick = () => {  
    setOverlayVisible(true);
  };

  const handleCloseOverlay = () => {
    setOverlayVisible(false);
  };

  return (
    
        <div className='flex flex-col bg-gray-50'>
          <div className="flex p-5 border-b justify-between items-center">
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
                    <BreadcrumbPage>Policies</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
            <div className="flex items-center space-x-2">
              <AccountCircleIcon />
              <p>John Doe</p>
            </div>
          </div>

          <div className='px-6'>
            <PoliciesTable onNewPolicyClick={handleNewPolicyClick} />
          </div>
          {isOverlayVisible && <NewPolicyOverlay onClose={handleCloseOverlay} />}
        </div>
     
  );
}
