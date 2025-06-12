import React from 'react';
import { Button } from '../../../components/ui/button';
import { CloudUploadIcon, X } from 'lucide-react';
import BackupIcon from '@mui/icons-material/Backup';

const NewApplicationOverlay = ({ onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/30  z-40 flex">
      <div className="fixed top-0 right-0 h-full w-1/3 shadow-lg z-50 p-6 bg-white">
       <div className='flex flex-col'>
       <div className='flex justify-between items-center'>
        <h1 className='text-2xl font-semibold'>Create New Application</h1>
        <Button className="cursor-pointer" variant="ghost" size="icon" onClick={onClose}>
            <X className="h-6 w-6" />
        </Button>
        </div>
        <div className='flex mt-4 cursor-pointer flex-col items-center justify-center bg-gray-100 rounded-lg h-70 '>
            <div className=''> <CloudUploadIcon className='text-gray-500' size={100} /></div>
            <div className='text-black font-sans font-semibold'>Upload & Attach Files</div>
        </div>
       </div>
      </div>
    </div>
  );
};

export default NewApplicationOverlay; 