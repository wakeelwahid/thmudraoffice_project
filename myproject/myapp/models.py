from django.db import models

# Create your models here.
from django.db import models

class CreateApprovalLetter(models.Model):
    FINANCE_TYPE_CHOICES = [
        ('mudra', 'Mudra Finance'),
        ('kreditbee', 'Kredit Bee'),
        ('indiabulls', 'IndiaBulls Dhani Finance'),
    ]

    finance_type = models.CharField(
        max_length=50,
        choices=FINANCE_TYPE_CHOICES,
        default='kreditbee',
        verbose_name="Finance Type"
    )
    DURATION_TYPE_CHOICES = [
        ('month', 'Month'),
        ('year', 'Year'),
    ]

    fullname = models.CharField(max_length=20)
    mobile = models.CharField(max_length=10)
    email = models.CharField(max_length=50)
    pancard = models.CharField(max_length=10)
    aadharcard = models.CharField(max_length=12)

    loanamount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Loan Amount (₹)")
    interest = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Interest Rate (%)")
    
    loan_duration_value = models.PositiveIntegerField(verbose_name="Loan Duration")
    loan_duration_type = models.CharField(
        max_length=5,
        choices=DURATION_TYPE_CHOICES,
        default='month',
        verbose_name="Duration Type"
    )

    insurance = models.CharField(
        max_length=50,
        verbose_name="Insurance Charge Refund"  # Now free text input
    )

    customeraccount = models.CharField(max_length=20)
    customername = models.CharField(max_length=20)
    ifsc = models.CharField(max_length=20)
    branchname = models.CharField(max_length=50)
    company_account_name = models.CharField(max_length=100, blank=True, null=True)
    company_account_number = models.CharField(max_length=30, blank=True, null=True)
    company_ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    company_branch_name = models.CharField(max_length=50, blank=True, null=True)
    
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)


    def __str__(self):
        return self.fullname

    def get_full_loan_duration(self):
        return f"{self.loan_duration_value} {self.loan_duration_type}(s)"



from django.db import models

class BankDetail(models.Model):
    account_name = models.CharField(max_length=100, verbose_name="account_name")
    account_number = models.CharField(max_length=30, verbose_name="account_number")
    ifsc_code = models.CharField(max_length=20, verbose_name="ifsc_code")
    branch_name = models.CharField(max_length=50, verbose_name="branch_name")
    

    def __str__(self):
        return f"{self.bank_name} - {self.loan_account_no}"

  

# class ApprovalLetter(models.Model):

#     finance_type = models.CharField(
#         max_length=50,
#         choices=[
#             ('mudra', 'Mudra Finance'),
#             ('kreditbee', 'Kredit Bee'),
#             ('indiabulls', 'IndiaBulls Dhani Finance'),
#         ],
#         default='kreditbee'
#     )