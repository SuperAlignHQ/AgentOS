from utils.payslip import payslip_prompt
from utils.driving_license import driving_license_prompt
from utils.passport import passport_prompt
from utils.p60 import p60_prompt
from utils.bank_statement import bank_statement_prompt

mapping={"bank_statements":bank_statement_prompt,
 "payslip":payslip_prompt,
 "passport":passport_prompt,
 "driving_license":driving_license_prompt,
 "p60":p60_prompt}

def get_prompt_for_type(typ:str)-> str:
    return mapping.get(typ)
