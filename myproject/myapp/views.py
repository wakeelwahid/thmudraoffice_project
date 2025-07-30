# Edit Approval Letter View
from .forms import PersonaldetailsForm
from .models import CreateApprovalLetter
from django.shortcuts import render, get_object_or_404, redirect

def edit_letter(request, pk):
    letter = get_object_or_404(CreateApprovalLetter, pk=pk)
    if request.method == "POST":
        form = PersonaldetailsForm(request.POST, request.FILES, instance=letter)
        if form.is_valid():
            form.save()
            return redirect('approvalletter')
    else:
        form = PersonaldetailsForm(instance=letter)
    # For dropdowns, etc. (if needed)
    banks = []
    try:
        from .models import BankDetail
        banks = BankDetail.objects.values_list('account_name', flat=True).distinct()
    except:
        pass
    return render(request, 'home.html', {'form': form, 'banks': banks, 'edit_mode': True, 'letter': letter})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse

from .forms import BankDetailForm, PersonaldetailsForm
from .models import BankDetail, CreateApprovalLetter

# ------------------------
# 1. Home / Letter Creation
# ------------------------
from .models import BankDetail

def create_letter(request):
    if request.method == "POST":
        form = PersonaldetailsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Details successfully saved.")
            return redirect('create_letter')
        else:
            messages.error(request, "❌ Form contains errors. Please correct them.")
    else:
        form = PersonaldetailsForm()

    # ✅ Get unique bank names
    banks = BankDetail.objects.values_list('account_name', flat=True).distinct()

    return render(request, 'home.html', {'form': form, 'banks': banks})



# ------------------------
# 2. EMI Calculator Page
# ------------------------
def emiCalculator(request):
    return render(request, 'emi-calculator.html')


# ------------------------
# 3. Dashboard Page
# ------------------------
def dashboard(request):
    return render(request, "dashboard.html")


# ------------------------
# 4. Approval Letter Listing
# ------------------------
def approvalletter(request):
    list = CreateApprovalLetter.objects.all()
    return render(request, "approvalletter.html", {'list': list})


# ------------------------
# 5. Add Bank
# ------------------------
def addbank(request):
    if request.method == 'POST':
        form = BankDetailForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Bank details successfully saved.")
            return redirect('addbank')
    else:
        form = BankDetailForm()

    # Get unique bank names for dropdown (for dynamic form)
    banks = BankDetail.objects.all().values_list('account_name', flat=True).distinct()
    return render(request, 'addbank.html', {'form': form, 'banks': banks})


# ------------------------
# 6. Show All Banks
# ------------------------
def show_banks(request):
    banks = BankDetail.objects.all()
    return render(request, 'show_banks.html', {'banks': banks})


# ------------------------
# 7. Edit Bank
# ------------------------
def edit_bank(request, pk):
    bank = get_object_or_404(BankDetail, pk=pk)
    if request.method == 'POST':
        form = BankDetailForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Bank details updated successfully.")
            return redirect('show_banks')
    else:
        form = BankDetailForm(instance=bank)
    return render(request, 'edit_bank.html', {'form': form})


# ------------------------
# 8. Delete Bank
# ------------------------
def delete_bank(request, pk):
    bank = get_object_or_404(BankDetail, pk=pk)
    bank.delete()
    messages.success(request, "🗑️ Bank deleted successfully.")
    return redirect('show_banks')


# ------------------------
# 9. AJAX - Get Bank Details by Name
# ------------------------
def get_bank_details(request):
    bank_name = request.GET.get('bank_name')
    try:
        bank = BankDetail.objects.get(account_name__iexact=bank_name)
        data = {
            'account_number':bank.account_number,
            'ifsc_code': bank.ifsc_code,
            'branch_name': bank.branch_name
        }
        return JsonResponse(data)
    except BankDetail.DoesNotExist:
        return JsonResponse({'error': 'Bank not found'}, status=404)
    
# views.py

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders
from django.shortcuts import get_object_or_404
from weasyprint import HTML
from .models import CreateApprovalLetter
from django.conf import settings
import os
import datetime
import urllib.parse

def absolute_static(path):
    full_path = finders.find(path)
    if not full_path:
        raise FileNotFoundError(f"{path} not found")
    # Use file:/// and forward slashes, no encoding for WeasyPrint
    url_path = os.path.abspath(full_path).replace("\\", "/")
    return f"file:///{url_path}"

def download_pdf(request, pk):
    data = get_object_or_404(CreateApprovalLetter, pk=pk)

    def calculate_emi(P, R, N):
        r = float(R) / 12 / 100
        emi = (float(P) * r * (1 + r) ** N) / ((1 + r) ** N - 1) if r > 0 else float(P) / N
        return round(emi, 2)

    def generate_schedule(P, R, N, emi):
        schedule = []
        balance = float(P)
        r = float(R) / 12 / 100
        for i in range(1, N + 1):
            interest = round(balance * r, 2)
            principal = round(emi - interest, 2)
            if i == N:
                principal = balance
                emi = principal + interest
            balance = round(balance - principal, 2)
            schedule.append({
                'month': i,
                'balance': f"{max(balance,0):,.2f}",
                'principal': f"{principal:,.2f}",
                'interest': f"{interest:,.2f}",
                'payment': f"{emi:,.2f}",
            })
        return schedule

    P = float(data.loanamount)
    R = float(data.interest)
    N = int(data.loan_duration_value) * 12 if data.loan_duration_type == 'year' else int(data.loan_duration_value)

    emi = calculate_emi(P, R, N)
    total_payable = round(emi * N, 2)
    interest_payable = round(total_payable - P, 2)
    schedule = generate_schedule(P, R, N, emi)

    # Dynamically select images based on finance_type
    # Use POSTed value if present, else use model field
    if request.method == 'POST' and request.POST.get('finance_type'):
        finance_type = request.POST.get('finance_type').lower()
    else:
        finance_type = data.finance_type.lower()

    import os
    
    if finance_type == "mudra":
        logo_path = absolute_static('images/mudra_logo.png')
        barcode_path = absolute_static('images/pmmy_barcode.gif')
    elif finance_type == "indiabulls":
        logo_path = absolute_static('images/indiabulls_logo.png')
        barcode_path = absolute_static('images/ibdf_barcode.gif')
    else:  # kreditbee or default
        logo_path = absolute_static('images/kreditbeescrren.png')
        barcode_path = absolute_static('images/ibdf_barcode.gif')

 
            

    

    # Common images
    sign1 = absolute_static('images/stampp.png')
    sign2 = absolute_static('images/Untitled 1.png')
    sign3 = absolute_static('images/stamp_invoice.png')
    sign4 = absolute_static('images/signatory_invoice.png')

    # Dynamic KYC verification logic
    import random
    today_str = datetime.date.today().strftime("%Y%m%d")
    random_digits = str(random.randint(1000, 9999))
    if finance_type == "mudra":
        title = "Pradhan Mantri MUDRA Yojana"
        kyc_verification = f"PMMY/{today_str}/{random_digits}"
    elif finance_type == "kreditbee":
        title = "Kredit Bee Finance"
        kyc_verification = f"KRDB/{today_str}/{random_digits}"
    elif finance_type == "indiabulls":
        title = "IndiaBulls Dhani Finance"
        kyc_verification = f"INDB/{today_str}/{random_digits}"
    else:
        kyc_verification = getattr(data, "pancard", "")

    context = {
        "data": {
            "fullname": data.fullname,
            "kyc_verification": kyc_verification,
            "loan_amount": data.loanamount,
            "emi": emi,
            "interest_rate": data.interest,
            "insurance_charge": data.insurance,
            "account_number": data.customeraccount,
            "branch_name": data.branchname,
            "ifsc_code": data.ifsc,
            "period": data.get_full_loan_duration(),
            "date": datetime.date.today(),
            "interest_payable": interest_payable,
            "total_payable": total_payable,
            "repayment_schedule": schedule,
            "company_account_name": data.company_account_name,
            "company_account_number": data.company_account_number,
            "company_ifsc_code": data.company_ifsc_code,
            "company_branch_name": data.company_branch_name,
            "title":title
        },
        "logo_path": logo_path,
        "barcode_path": barcode_path,
        "sign1": sign1,
        "sign2": sign2,
        "sign3": sign3,
        "sign4": sign4,
    }

    html_string = render_to_string("pdf_template.html", context)
    static_base = os.path.join(settings.BASE_DIR, 'myapp', 'static')
    html = HTML(string=html_string, base_url=static_base)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="approval_letter_{data.fullname}.pdf"'
    return response
