import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import { CalendarIcon } from "lucide-react"

const FormField = ({ label, value, hasCalendar = false }) => (
  <div className="space-y-1">
    <Label htmlFor={label}>{label}</Label>
    <div className="relative">
      <Input id={label} defaultValue={value} />
      {hasCalendar && (
        <CalendarIcon className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
      )}
    </div>
  </div>
);

const FormRow = ({ children }) => (
    <div className="grid grid-cols-2 gap-6">
        {children}
    </div>
)

const triggerClasses = "text-black/50  cursor-pointer rounded-full bg-black/5 data-[state=active]:bg-black data-[state=active]:text-white"

export function TabsDemo() {
    return (
    <Tabs defaultValue="memo" className="">
        <TabsList className="flex space-x-2 rounded-lg bg-white">
            <TabsTrigger value="memo" className={triggerClasses}>Memo</TabsTrigger>
            <TabsTrigger value="passport" className={triggerClasses}>Passport</TabsTrigger>
            <TabsTrigger value="p60" className={triggerClasses}>P60</TabsTrigger>
            <TabsTrigger value="salary_slip" className={triggerClasses}>Salary Slip</TabsTrigger>
            <TabsTrigger value="bank_statement" className={triggerClasses}>Bank Statement</TabsTrigger>
        </TabsList>
      
      {/* Memo Tab */}
      <TabsContent value="memo" className="mt-2">
        <form className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="outstanding">Outstanding</Label>
                    <Input className="h-12 text-gray-500" id="outstanding" defaultValue="107185703" />
                </div>
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="referral">Referral Reason / Code</Label>
                    <Input className="h-12 text-gray-500" id="referral" defaultValue="107185703" />
                </div>
            </div>
            <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="lending">Lending Details</Label>
                    <Input className="h-12 text-gray-500" id="lending" defaultValue="107185703" />
                </div>
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="deposit">Deposit / Holding</Label>
                    <Input className="h-12 text-gray-500" id="deposit" defaultValue="107185703" />
                </div>
            </div>
            <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="income_verified">Income Verified as Declared</Label>
                    <Input className="h-12 text-gray-500" id="income_verified" defaultValue="107185703" />
                </div>
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="outgoings_verified">Outgoings Verified as Declared</Label>
                    <Input className="h-12 text-gray-500" id="outgoings_verified" defaultValue="107185703" />
                </div>
            </div>
            <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="bank_observations">Bank Statement Observations</Label>
                    <Input className="h-12 text-gray-500" id="bank_observations" defaultValue="107185703" />
                </div>
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="salary_evidenced">Salary Credit Evidenced</Label>
                    <Input className="h-12 text-gray-500" id="salary_evidenced" defaultValue="107185703" />
                </div>
            </div>
            <div className="space-y-2">
                <Label className="text-lg text-black/70" htmlFor="justification">Justification for Decision</Label>
                <Input className="h-24 text-gray-500" id="justification" />
            </div>
        </form>
      </TabsContent>

      {/* Passport Tab */}
      <TabsContent value="passport" className="mt-2">
        <form className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
                <Label className="text-lg text-black/70" htmlFor="full_name">Full Name</Label>
                <Input className="h-12 text-gray-500" id="full_name" defaultValue="Jodice Pippa" />
            </div>
            <div className="space-y-2">
                <Label className="text-lg text-black/70" htmlFor="dob">Date of Birth</Label>
                <div className="relative">
                    <Input className="h-12 text-gray-500" id="dob" defaultValue="01/02/1993" />
                    <CalendarIcon className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                </div>
            </div>
          </div>
          <div className="space-y-2">
              <Label className="text-lg text-black/70" htmlFor="passport_number">Passport Number</Label>
              <Input className="h-12 text-gray-500" id="passport_number" defaultValue="107185703" />
          </div>
           <div className="space-y-2">
              <Label className="text-lg text-black/70" htmlFor="address">Address</Label>
              <Input className="h-12 text-gray-500" id="address" defaultValue="123 Main Street" />
          </div>
        </form>
      </TabsContent>
      
      {/* P60 Tab */}
        <TabsContent value="p60" className="mt-2">
            <form className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="p60_employee_name">Employee Name</Label>
                        <Input className="h-12 text-gray-500" id="p60_employee_name" defaultValue="Jodice Pippa" />
                    </div>
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="p60_employer_name">Employer Name</Label>
                        <Input className="h-12 text-gray-500" id="p60_employer_name" defaultValue="Jodice Pippa" />
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="p60_date">Date/Year</Label>
                        <div className="relative">
                            <Input className="h-12 text-gray-500" id="p60_date" defaultValue="107185703" />
                            <CalendarIcon className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                        </div>
                    </div>
                </div>
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="p60_employee_address">Employee Address</Label>
                    <Input className="h-12 text-gray-500" id="p60_employee_address" defaultValue="123 Main Street" />
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="p60_ni">National Insurance No.</Label>
                        <Input className="h-12 text-gray-500" id="p60_ni" defaultValue="107185703" />
                    </div>
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="p60_deductions">Deductions</Label>
                        <Input className="h-12 text-gray-500" id="p60_deductions" defaultValue="107185703" />
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="p60_income_current">Income from current employer</Label>
                        <Input className="h-12 text-gray-500" id="p60_income_current" defaultValue="107185703" />
                    </div>
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="p60_income_previous">Income from previous employer</Label>
                        <Input className="h-12 text-gray-500" id="p60_income_previous" defaultValue="107185703" />
                    </div>
                </div>
            </form>
        </TabsContent>

        {/* Salary Slip Tab */}
        <TabsContent value="salary_slip" className="mt-2">
            <form className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="slip_employee_name">Employee Name</Label>
                        <Input className="h-12 text-gray-500" id="slip_employee_name" defaultValue="Jodice Pippa" />
                    </div>
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="slip_employer_name">Employer Name</Label>
                        <Input className="h-12 text-gray-500" id="slip_employer_name" defaultValue="Jodice Pippa" />
                    </div>
                </div>
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="address_salary">Address</Label>
                    <Input className="h-12 text-gray-500" id="address_salary" defaultValue="123 Main Street" />
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="slip_basic_income">Basic Income</Label>
                        <Input className="h-12 text-gray-500" id="slip_basic_income" defaultValue="107185703" />
                    </div>
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="slip_ytd_income">YTD Income</Label>
                        <Input className="h-12 text-gray-500" id="slip_ytd_income" defaultValue="107185703" />
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="slip_tax_period">Tax Period</Label>
                         <div className="relative">
                            <Input className="h-12 text-gray-500" id="slip_tax_period" defaultValue="107185703" />
                            <CalendarIcon className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                        </div>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="slip_deductions">Deductions</Label>
                        <Input className="h-12 text-gray-500" id="slip_deductions" defaultValue="107185703" />
                    </div>
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="slip_variable_income">Variable Income</Label>
                        <Input className="h-12 text-gray-500" id="slip_variable_income" defaultValue="10718570_ext" />
                    </div>
                </div>
            </form>
        </TabsContent>

      {/* Bank Statement Tab */}
        <TabsContent value="bank_statement" className="mt-2">
            <form className="space-y-6">
                <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="applicant_name">Applicant Name</Label>
                    <Input className="h-12 text-gray-500" id="applicant_name" defaultValue="Jodice Pippa" />
                </div>
                 <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="address_bank">Address</Label>
                    <Input className="h-12 text-gray-500" id="address_bank" defaultValue="123 Main Street" />
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="credits">Credits</Label>
                        <Input className="h-12 text-gray-500" id="credits" defaultValue="107185703" />
                    </div>
                    <div className="space-y-2">
                        <Label className="text-lg text-black/70" htmlFor="debits">Debits</Label>
                        <Input className="h-12 text-gray-500" id="debits" defaultValue="107185703" />
                    </div>
                </div>
                 <div className="space-y-2">
                    <Label className="text-lg text-black/70" htmlFor="match_salary">Match Salary Credits</Label>
                    <Input className="h-12 text-gray-500" id="match_salary" defaultValue="107185703" />
                </div>
            </form>
        </TabsContent>
    </Tabs>
  )
}
