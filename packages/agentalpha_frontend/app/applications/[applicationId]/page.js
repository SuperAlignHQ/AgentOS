"use client"

import React, { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Button } from "@/components/ui/button"
import SpeakerNotesIcon from '@mui/icons-material/SpeakerNotes';
import { DescriptionOutlined, Done, PhotoSizeSelectActualOutlined, SpeakerNotesOffOutlined, SpeakerNotesOutlined } from "@mui/icons-material";
import DoneIcon from '@mui/icons-material/Done';
import CloseIcon from '@mui/icons-material/Close';
import CreateIcon from '@mui/icons-material/Create';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { Checkbox } from "@/components/ui/checkbox"
import { TabsDemo } from "@/components/ApplicationTabs";
import { CloudUploadIcon, X } from "lucide-react";
import uploadedDocuments from "./uploadedDocuments.json";
import DocDetailOverlay from "@/components/DocDetailOverlay";

const ApplicationDetailPage = ({ params }) => {


    const router = useRouter();
    const { applicationId } = use(params);
    const [isNotesOpen, setIsNotesOpen] = useState(false);
    const [docDetailsOpen, setDocDetailsOpen] = useState(false);
    const [file, setFile] = useState(null);
    const [docCategory, setDocCategory] = useState(null);
    const [docStatus, setDocStatus] = useState(false);

    const handleDocStatus = (status) => {
        const [done, total] = status.split('/').map(Number);
       if(done === total){
        setDocStatus(true);
       }
       else{
        setDocStatus(false);
       }
    }
    useEffect(() => {
        if (isNotesOpen || docDetailsOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }

        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isNotesOpen, docDetailsOpen]);
    const displayStatus = (status) => {
        const [done, total] = status.split('/').map(Number);
        return done === total ?
            <DoneIcon className="rounded-full h-2 border text-green-500 border-green-500 p-1" /> :
            <CloseIcon className=" text-red-500 rounded-full h-2 border border-red-500 p-1" />;
    }
    return (
        <div className='flex flex-col bg-white no-scrollbar'>
            {/* Top Bar */}
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
                                <BreadcrumbLink asChild>
                                    <Link href="/applications">Applications</Link>
                                </BreadcrumbLink>
                            </BreadcrumbItem>
                            <BreadcrumbSeparator />
                            <BreadcrumbItem>
                                <BreadcrumbPage>{applicationId}</BreadcrumbPage>
                            </BreadcrumbItem>
                        </BreadcrumbList>
                    </Breadcrumb>
                </div>
                <div className="flex items-center space-x-2">
                    <AccountCircleIcon />
                    <p>John Doe</p>
                </div>
            </div>

            <div className='flex flex-col bg-black/5'>
                <div className="ml-8 mr-4 flex flex-col">
                    {/* Application Details */}
                    <div className="flex justify-between  mt-6 space-x-4 items-start">
                        <div className="flex gap-2">
                            <div onClick={() => router.back()} className="cursor-pointer">
                                <ArrowBackIcon fontSize="large" className="cursor-pointer hover:bg-black/5 hover:rounded-full p-1" />
                            </div>
                            <div className="flex flex-col gap-1 font-sans">
                                <div className="flex gap-4 items-center">
                                    <h1 className="text-2xl font-bold">Application Memo</h1>
                                    <Button className="rounded-full font-extralight text-sm h-7" >
                                        Flagged
                                    </Button>
                                </div>
                                <div className="flex gap-1 items-center">
                                    <p className="text-sm text-black/50">Application ID: {applicationId}</p>
                                    <p>.</p>
                                    <p className="text-sm text-black/50">Submitted Apr 10, 2025</p>
                                </div>
                            </div>
                        </div>
                        <div className="flex gap-4 items-center ">
                            <div onClick={() => { setIsNotesOpen(true) }}
                                className="hover:bg-black/5 hover:rounded-full p-2 cursor-pointer"><SpeakerNotesOutlined /></div>
                            <Button className="rounded-md cursor-pointer  font-extralight text-sm">
                                Approve
                                <DoneIcon className="text-white" />
                            </Button>
                            <button className=" bg-black/5 cursor-pointer border p-1 rounded-md items-center justify-center font-sans text-sm">
                                Reject
                                <CloseIcon className="text-black" />
                            </button>
                        </div>
                    </div>
                    {/* Uploaded Documents & Extracted Info */}
                    <div className="flex items-stretch gap-4 mt-6 mb-5">
                        {/* Uploaded Documents */}
                        <div className="flex w-1/4 flex-col   border bg-white border-gray-200 rounded-md p-4 gap-4 ">
                            <div className="flex justify-between items-center">
                                <h1 className="text-2xl font-semibold">Uploaded Documents</h1>
                                <CreateIcon fontSize="medium" />
                            </div>

                            {/* Identity Proof */}
                            {uploadedDocuments.uploadedDocuments.map((section, index) => (
                                <div key={index} className="flex flex-col w-full  border rounded-md mt-2 ">
                                    <div className="flex justify-between items-center p-4 bg-black/5 w-full">
                                        <div>{section.category}</div>
                                        <KeyboardArrowUpIcon />
                                    </div>
                                    {section.files.map((file, idx) => (
                                        <div onClick={() => {setDocDetailsOpen(true);
                                                           setFile(file);
                                                           setDocCategory(section.category);
                                                           handleDocStatus(file.status);
                                                           }}
                                            key={idx} className="flex cursor-pointer hover:bg-black/15 justify-between items-center p-4">
                                            <div className="flex w-full items-center   gap-2">
                                                {file.fileName.includes(".pdf") ?
                                                    <DescriptionOutlined fontSize="large" className="text-black/50" /> :
                                                    <PhotoSizeSelectActualOutlined fontSize="large" className="text-black/50" />
                                                }
                                                <div className="flex flex-col">
                                                    <p className="text-sg font-semibold">{file.fileName}</p>
                                                    <p className="text-xs text-black/50">
                                                        Uploaded on {file.uploadedOn} : {file.fileSize}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex flex-col items-center">
                                                {
                                                    displayStatus(file.status)
                                                }
                                                <div className="text-xs">{file.status}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ))}
                            {/* Income Proof */}
                            {/* <div className="flex flex-col w-full  border rounded-md mt-2 ">
                                <div className="flex justify-between items-center p-4 bg-gray-100 w-full">
                                    <div>Income Proof</div>
                                    <KeyboardArrowUpIcon />
                                </div>
                                <div className="flex flex-col w-full">

                                    <div className="flex justify-between items-center p-4">
                                        <div className="flex w-full items-center bg-white gap-2">
                                            <DescriptionOutlined fontSize="large" className="text-gray-500" />
                                            <div className="flex flex-col">
                                                <p className="text-sg font-semibold">Passport.pdf</p>
                                                <p className="text-xs text-gray-500">Uploaded on Apr 10, 2025 : 2 MB</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-col">
                                            <Checkbox id="IdProof" className="rounded-full" />
                                            <div className="text-xs">4/4</div>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center p-4">
                                        <div className="flex w-full items-center bg-white gap-2">
                                            <DescriptionOutlined fontSize="large" className="text-gray-500" />
                                            <div className="flex flex-col">
                                                <p className="text-sg font-semibold">Passport.pdf</p>
                                                <p className="text-xs text-gray-500">Uploaded on Apr 10, 2025 : 2 MB</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-col">
                                            <Checkbox id="IdProof" className="rounded-full" />
                                            <div className="text-xs">4/4</div>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center p-4">
                                        <div className="flex w-full items-center bg-white gap-2">
                                            <DescriptionOutlined fontSize="large" className="text-gray-500" />
                                            <div className="flex flex-col">
                                                <p className="text-sg font-semibold">Passport.pdf</p>
                                                <p className="text-xs text-gray-500">Uploaded on Apr 10, 2025 : 2 MB</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-col">
                                            <Checkbox id="IdProof" className="rounded-full" />
                                            <div className="text-xs">4/4</div>
                                        </div>
                                    </div>


                                </div>
                            </div> */}
                            {/* Uncategorized */}
                            {/* <div className="flex flex-col w-full  border rounded-md mt-2 ">
                                <div className="flex justify-between items-center p-4 bg-gray-100 w-full">
                                    <div>Identity Proof</div>
                                    <KeyboardArrowUpIcon />
                                </div>
                                <div className="flex justify-between items-center  p-4">
                                    <div className="flex w-full items-center bg-white gap-2">
                                        <PhotoSizeSelectActualOutlined fontSize="large" className="text-gray-500" />
                                        <div className="flex flex-col">
                                            <p className="text-sg font-semibold">Image.jpg</p>
                                            <p className="text-xs text-gray-500">Uploaded on Apr 10, 2025 : 2 MB</p>
                                        </div>
                                    </div>
                                    <div className="flex flex-col">
                                        <Checkbox id="IdProof" className="rounded-full" />
                                        <div className="text-xs">4/4</div>
                                    </div>
                                </div>
                            </div> */}
                        </div>
                        {/* Extracted Information */}
                        <div className="flex flex-col w-3/4">
                            <div className="flex w-full flex-col border max-h-[80vh] min-h-[75vh] overflow-y-auto no-scrollbar bg-white border-gray-200 rounded-md p-4 gap-4 ">
                                <div className="flex justify-between items-center">
                                    <h2 className="text-3xl font-semibold">Extracted Information</h2>
                                    <CreateIcon fontSize="medium" />
                                </div>
                                <div>
                                    <TabsDemo />
                                </div>
                            </div>
                            <div className="flex flex-col w-full mt-4 bg-white border border-gray-200 rounded-md p-4 gap-4">
                                <div className="text-black font-semibold">Add Notes ...</div>
                                <textarea className="w-full h-24 border bg-black/5 text-sm  rounded-md p-2" placeholder="Add Notes..." />
                            </div>
                        </div>


                    </div>


                </div>
            </div>
            {isNotesOpen && (
                <div className="fixed inset-0 bg-black/65 bg-opacity-50 flex justify-center items-center">
                    <div className="fixed top-0 right-0 h-full w-1/3 shadow-lg z-50 p-6 bg-white">
                        <div className='flex flex-col'>
                            <div className='flex justify-between items-center'>
                                <h1 className='text-2xl font-semibold'>Add Application Notes</h1>
                                <Button className="cursor-pointer" variant="ghost" size="icon" onClick={() => { setIsNotesOpen(false) }}>
                                    <X className="h-6 w-6" />
                                </Button>
                            </div>
                            <textarea className='flex mt-4 focus:outline-none p-3 text-sm flex-col items-center justify-center bg-black/5 rounded-lg h-70 ' placeholder="Add Notes..." />
                        </div>
                    </div>
                </div>
            )}
           
            {
                docDetailsOpen && (
                    <DocDetailOverlay doc={file} onClose={() => setDocDetailsOpen(false)} category={docCategory} status={docStatus} />
                )
            }
        </div>
    );
};

export default ApplicationDetailPage;
