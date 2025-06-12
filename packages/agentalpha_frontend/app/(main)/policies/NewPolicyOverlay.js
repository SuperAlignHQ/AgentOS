import { X } from 'lucide-react'
import React, { useState } from 'react'
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from "@/components/ui/select"
const NewPolicyOverlay = ({onClose}) => {
    const [documentType, setDocumentType] = useState('');
    const [policyPhase, setPolicyPhase] = useState('');
  return (
    <div className="fixed inset-0 bg-black/30 z-40 flex">
      <div className="fixed top-0 right-0 h-full w-1/3 shadow-lg z-50 p-6 bg-white">
      <div className='flex flex-col'>
        <div className='flex justify-between items-center'>
            <h1 className='text-2xl font-semibold'>Create New Policy</h1>
            <Button className="cursor-pointer" variant="ghost" size="icon" onClick={onClose}>
                <X className="h-6 w-6" />
            </Button>
        </div>
        <div className='flex flex-col mt-4 gap-4'>
        <div>
        <label className='text-md font-semibold '>Policy Name</label>
        <Input className='w-full mt-2 bg-gray-100 rounded-md focus:outline-none p-4 border-none h-12 ' placeholder='Policy Name' />
        </div>
        <div>
        <label className='text-sm font-semibold '>Prompt for policy</label>
        <textarea className='w-full mt-2 bg-gray-100 rounded-md focus:outline-none p-4 border-none  ' placeholder='Prompt for policy' />
        </div>
        <div>
        <label className='text-sm font-semibold'>Document Type</label>
        <Select value={documentType} onValueChange={setDocumentType}>
            <SelectTrigger className='w-full mt-2 bg-gray-100 rounded-md focus:outline-none p-4 border-none h-12 '>
                <SelectValue placeholder='Select Document Type' />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value='P60'>P60</SelectItem>
                <SelectItem value='Passport'>Passport</SelectItem>
                <SelectItem value='Payslip'>Payslip</SelectItem>
                <SelectItem value='Bank Statement'>Bank Statement</SelectItem>
                <SelectItem value='Other'>Other</SelectItem>

            </SelectContent>
        </Select>
        </div>
        <div>
        <label className='text-sm font-semibold'>Policy phase</label>
        <Select className='w-full mt-2 bg-gray-100 rounded-md focus:outline-none p-4 border-none h-12 ' value={policyPhase} onValueChange={setPolicyPhase}>
            <SelectTrigger className='w-full mt-2 bg-gray-100 rounded-md focus:outline-none p-4 border-none h-12 '>
                <SelectValue placeholder='Select Policy Phase' />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value='Testing'>Testing</SelectItem>
                <SelectItem value='Production'>Production</SelectItem>
            </SelectContent>
        </Select>
        </div>
        </div>
        <Button  className='w-1/4  mt-6 bg-black cursor-pointer text-white rounded-md focus:outline-none p-4 border-none h-12 '>Create Policy</Button>
      </div>
      </div>
      </div>
  )
}

export default NewPolicyOverlay
