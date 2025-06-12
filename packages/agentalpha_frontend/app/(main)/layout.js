import Sidebar from "@/components/Sidebar";

export default function MainLayout({ children }) {
  return (
    <>
        <Sidebar />
        <div className="flex-1 ml-63">
          {children}
        </div>
    </>
  );
} 