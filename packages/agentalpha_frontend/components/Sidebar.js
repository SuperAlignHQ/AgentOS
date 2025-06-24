'use client'
import React, { useEffect, useState } from 'react'
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
  } from "@/components/ui/select"
import PublicIcon from '@mui/icons-material/Public';
import SearchIcon from '@mui/icons-material/Search';
import SaveAsIcon from '@mui/icons-material/SaveAs';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DescriptionIcon from '@mui/icons-material/Description';
import SafetyCheckIcon from '@mui/icons-material/SafetyCheck';
import { useRouter, usePathname } from 'next/navigation';
import { DashboardOutlined, DescriptionOutlined, SafetyCheckOutlined, SaveAsOutlined } from '@mui/icons-material';

const Sidebar = () => {
  const router = useRouter()
  const pathname = usePathname()
  const [country, setCountry] = useState('uk')
  const [isOpen, setIsOpen] = useState(true)
  const [isOpen2, setIsOpen2] = useState(pathname === '/dashboard')
  const [isOpen3, setIsOpen3] = useState(pathname === '/applications')
  const [isOpen4, setIsOpen4] = useState(pathname === '/policies')
  const handleClick = () => {
    router.push('/dashboard')
     setIsOpen2(true)
     setIsOpen3(false)
     setIsOpen4(false)
  }
  const handleClick2 = () => {
    router.push('/applications')
    setIsOpen3(true)
    setIsOpen2(false)
    setIsOpen4(false)
  }

  useEffect(() => {
    setIsOpen2(pathname === '/dashboard')
    setIsOpen3(pathname === '/applications')
    setIsOpen4(pathname === '/policies')
  }, [pathname])

  return (
    <div className='fixed flex flex-col w-1/6 p-4 h-screen border-r bg-white z-10'> 
    <div className='mt-4'>
     <Select className='text-black' value={country} onValueChange={setCountry}>
      <SelectTrigger className="w-full text-black font-semibold">
        <SelectValue placeholder="Select a Country" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectItem  value="uk"><PublicIcon className='text-black' /> UK Market</SelectItem>
          <SelectItem value="us"><PublicIcon className='text-black' /> US Market</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>     
    </div>
    <div className=' relative mt-4'>
       <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600" />
        <input type="text" placeholder="Search" className='w-full p-2 pl-10 rounded-md border border-gray-300 focus:outline-none' />
    </div>

    <div onClick={() => setIsOpen(!isOpen)} className={`flex mt-4 justify-between hover:bg-black/5 p-2 rounded-md cursor-pointer ${isOpen ? '' : 'bg-black/15'}`}>
         <div className='flex space-x-2 items-center'>
            {!isOpen ? <SaveAsIcon className='text-black' /> : <SaveAsOutlined className='text-black' />}
        <p className='text-black font-semibold'>Secured Learning</p>
        </div>
        <div>
       {isOpen && <div><KeyboardArrowDownIcon className='text-black' /></div>}
       {!isOpen && <div> <KeyboardArrowUpIcon className='text-black' /> </div>}
        </div>
    </div>
    {!isOpen && (
            <div className='mt-4 pl-6 flex flex-col space-y-2'>
                <div onClick={handleClick} className={`flex space-x-2 items-center  cursor-pointer hover:bg-black/5 p-2 rounded-md ${isOpen2 ? 'bg-black/15 text-black' : ''}`}>
                 {!isOpen2 ? <DashboardOutlined /> : <DashboardIcon />}
                 <div className='text-sm'> Dashboard</div>
                </div>
                <div onClick={handleClick2} className={`flex space-x-2 items-center cursor-pointer hover:bg-black/5 p-2  rounded-md ${isOpen3 ? 'bg-black/15 text-black' : ''}`}>
                 {!isOpen3 ? <DescriptionOutlined /> : <DescriptionIcon />}
                  <div className='text-sm'> Applications </div>
                </div>
            </div>
        )}

      <div onClick={()=>router.push('/policies')}
       className={`flex space-x-2 mt-2 items-center cursor-pointer hover:bg-black/5 p-2  rounded-md ${isOpen4 ? 'bg-black/15 font-semibold' : ''}`}>
       {isOpen4 ? <SafetyCheckOutlined /> : <SafetyCheckIcon />}
        <div>Policies</div>
      </div>  
    </div>


  )
}

export default Sidebar
