'use client'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import Link from 'next/link'
import React, { useEffect, useState } from 'react'
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { ApplicationTable } from './ApplicationTable';
import NewApplicationOverlay from './NewApplicationOverlay';

const ApplicationsPage = () => {
  const [isOverlayVisible, setOverlayVisible] = useState(false);

  const handleNewApplicationClick = () => {
    setOverlayVisible(true);
  };

  const handleCloseOverlay = () => {

    setOverlayVisible(false);
  };

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
    <div className='flex flex-col bg-black/5'>
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
                <BreadcrumbPage>Applications</BreadcrumbPage>
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
        <ApplicationTable onNewApplicationClick={handleNewApplicationClick} />
      </div>
      {isOverlayVisible && <NewApplicationOverlay onClose={handleCloseOverlay} />}
    </div>
  )
}

export default ApplicationsPage
