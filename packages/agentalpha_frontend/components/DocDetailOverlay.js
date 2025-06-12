import React from 'react';
import { Button } from './ui/button';
import { X } from 'lucide-react';
import { DescriptionOutlined, PhotoSizeSelectActualOutlined } from '@mui/icons-material';
import DoneIcon from '@mui/icons-material/Done';
import CloseIcon from '@mui/icons-material/Close';
const DocDetailOverlay = ({ doc, onClose, category,status }) => {
  if (!doc) return null;

  return (
    <div className="fixed inset-0 bg-black/65 bg-opacity-50 flex justify-center items-center">
      <div className="fixed top-0 right-0 h-full w-1/3 shadow-lg z-50 p-6 bg-white">
        <div className='flex flex-col'>
          <div className='flex justify-between items-center'>
            <h1 className='text-2xl font-semibold'>Document Details</h1>
            <Button className="cursor-pointer" variant="ghost" size="icon" onClick={onClose}>
              <X className="h-6 w-6" />
            </Button>
          </div>
          <div className="flex w-full items-center bg-white gap-2">
            {doc.fileName.includes(".pdf") ?
              <DescriptionOutlined fontSize="large" className="text-black/50" /> :
              <PhotoSizeSelectActualOutlined fontSize="large" className="text-black/50" />
            }
            <div className="flex flex-col">
              <p className="text-sg font-semibold">{doc.fileName}</p>
              <p className="text-xs text-black/50">
                Uploaded on {doc.uploadedOn} : {doc.fileSize}
              </p>
            </div>
            <div>{status ? <Button>Passed</Button>:<Button>Failed</Button>}</div>
          </div>
          

        </div>
      </div>
    </div>
  );
};

export default DocDetailOverlay; 