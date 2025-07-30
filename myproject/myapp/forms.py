from django import forms
from .models import BankDetail,CreateApprovalLetter

class BankDetailForm(forms.ModelForm):
    class Meta:
        model = BankDetail
        fields = ['account_name', 'account_number', 'ifsc_code', 'branch_name']

class PersonaldetailsForm(forms.ModelForm):
    class Meta:
        model = CreateApprovalLetter
        fields = [
            'fullname','mobile','email','pancard','aadharcard','loanamount','interest',
            'loan_duration_type','loan_duration_value','insurance','customeraccount','customername',
            'ifsc','branchname','photo','company_account_name','company_account_number',
            'company_ifsc_code','company_branch_name','finance_type'
        ]


