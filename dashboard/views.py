from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
from django.core.files import File
import os
import requests
import hashlib

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .models import Testator, Beneficiary, Will, Asset, AssetDistribution, DeathCertificate
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
import uuid
from datetime import date
from reportlab.lib.pagesizes import A4  

# ================= IPFS =================
def upload_to_ipfs(file_path):
    try:
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

        headers = {
            "pinata_api_key": settings.PINATA_API_KEY,
            "pinata_secret_api_key": settings.PINATA_SECRET_API_KEY,
        }

        with open(file_path, "rb") as f:
            res = requests.post(url, files={"file": f}, headers=headers)

        return res.json().get("IpfsHash", "")
    except:
        return "IPFS_FAILED"


# ================= SIGN =================
def falcon_sign(data):
    signature = hashlib.sha256(data).hexdigest().encode()
    public_key = b"falcon_public_key"
    return signature, public_key


# ================= CREATE WILL =================
def create_will(request):
    testators = Testator.objects.all()
    beneficiaries = Beneficiary.objects.all()

    selected_testator = request.POST.get("testator")

    assets = []
    if selected_testator:
        assets = Asset.objects.filter(owner_id=selected_testator)

    if request.method == "POST" and request.POST.get("asset_name"):
        testator = get_object_or_404(Testator, id=selected_testator)

        will = Will.objects.create(testator=testator)
        will.beneficiaries.set(request.POST.getlist("beneficiary_name"))

        asset_ids = request.POST.getlist("asset_name")
        beneficiary_ids = request.POST.getlist("beneficiary_name")
        share = request.POST.getlist("share")

        for i in range(len(asset_ids)):
            if asset_ids[i]:
                AssetDistribution.objects.create(
                    will=will,
                    asset_id=asset_ids[i],
                    beneficiary_id=beneficiary_ids[i],
                    share=share[i]
                )

        generate_will_pdf(will)

        return redirect("will_detail", pk=will.pk)

    return render(request, "dashboard/create_will.html", {
        "testators": testators,
        "beneficiaries": beneficiaries,
        "assets": assets,
        "selected_testator": selected_testator
    })


# ================= WILL DETAIL =================
def will_detail(request, pk):
    will = get_object_or_404(Will, pk=pk)
    distributions = AssetDistribution.objects.filter(will=will)

    return render(request, "dashboard/will_detail.html", {
        "will": will,
        "distributions": distributions
    })


# ================= GENERATE PDF =================
def generate_will_pdf(will):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from django.core.files import File
    import os

    file_path = os.path.join("media/wills", f"will_{will.id}.pdf")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    # ===== TITLE =====
    elements.append(Paragraph("<b>DIGITAL WILL</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    # ===== TESTATOR DETAILS =====
    elements.append(Paragraph(f"Testator Name : {will.testator.name}", styles["Normal"]))
    elements.append(Paragraph(f"Email : {will.testator.email}", styles["Normal"]))
    elements.append(Paragraph(f"Wallet : 0xXXXXXXXXXXXXXXX", styles["Normal"]))  # static or add field
    elements.append(Spacer(1, 20))

    # ===== BENEFICIARIES =====
    elements.append(Paragraph("<b>Beneficiaries:</b>", styles["Heading2"]))
    for b in will.beneficiaries.all():
        elements.append(Paragraph(f"- {b.name}", styles["Normal"]))

    elements.append(Spacer(1, 20))

    # ===== ASSETS =====
    elements.append(Paragraph("<b>Assets:</b>", styles["Heading2"]))
    for d in will.assetdistribution_set.all():
        elements.append(Paragraph(
            f"- {d.asset.name} | Value: {d.asset.value}",
            styles["Normal"]
        ))

    elements.append(Spacer(1, 30))

    # ===== NOTE =====
    elements.append(Paragraph(
        "<i>Note: This will is executed only after verified death via oracle.</i>",
        styles["Normal"]
    ))

    doc.build(elements)

    # SAVE PDF
    with open(file_path, "rb") as f:
        will.will_document.save(f"will_{will.id}.pdf", File(f), save=True)

    # ===== SIGN + IPFS =====
    import hashlib
    with open(file_path, "rb") as f:
        data = f.read()

    signature = hashlib.sha256(data).hexdigest()
    will.pq_signature = signature
    will.save()

    try:
        import requests
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": settings.PINATA_API_KEY,
            "pinata_secret_api_key": settings.PINATA_SECRET_API_KEY,
        }
        res = requests.post(url, files={"file": open(file_path, "rb")}, headers=headers)
        will.ipfs_hash = res.json().get("IpfsHash", "")
    except:
        will.ipfs_hash = "IPFS_FAILED"

    will.save()


# ================= CLAIM =================
@transaction.atomic
def claim_inheritance(request, will_id):
    will = get_object_or_404(Will, id=will_id)

    dc = DeathCertificate.objects.filter(will=will).first()

    #  No certificate
    if not dc:
        return HttpResponse("❌ Death Certificate not found")

    #  Aadhaar mismatch
    if dc.aadhaar != will.testator.aadhaar:
        return HttpResponse("❌ Aadhaar mismatch. Cannot claim assets.")

    #  Not verified
    if dc.status != "VERIFIED":
        return HttpResponse("❌ Death certificate not verified")

    #  SUCCESS
    return HttpResponse("✅ Assets transferred successfully to beneficiaries")
# ================= EXTRA FUNCTIONS (FIX ERRORS) =================

def admin_dashboard(request):
    return redirect('create_will')


def testator_detail(request, testator_id):
    testator = get_object_or_404(Testator, id=testator_id)
    return render(request, "dashboard/testator_detail.html", {"testator": testator})


def beneficiary_dashboard(request):
    beneficiaries = Beneficiary.objects.all()
    return render(request, "dashboard/beneficiary_dashboard.html", {"beneficiaries": beneficiaries})


def activate_will(request, will_id):
    will = get_object_or_404(Will, id=will_id)
    will.status = "ACTIVE"
    will.save()
    return redirect('will_detail', pk=will.id)

def add_distribution(request, pk):
    will = get_object_or_404(Will, pk=pk)

    if request.method == "POST":
        asset_id = request.POST.get("asset")
        beneficiary_id = request.POST.get("beneficiary")
        share = request.POST.get("share")

        #  VALIDATION (important)
        if not asset_id or not beneficiary_id or not share:
            return redirect('add_distribution', pk=pk)

        AssetDistribution.objects.create(
            will=will,
            asset_id=asset_id,
            beneficiary_id=beneficiary_id,
            share=float(share)   # ✅ ensure number
        )

        #  OPTIONAL: regenerate PDF after adding distribution
        generate_will_pdf(will)

        return redirect('will_detail', pk=pk)

    #  Only show testator assets
    assets = Asset.objects.filter(owner=will.testator)

    #  Only selected beneficiaries (better logic)
    beneficiaries = will.beneficiaries.all()

    return render(request, "dashboard/add_distribution.html", {
        "will": will,
        "assets": assets,
        "beneficiaries": beneficiaries
    })
def generate_will_pdf_view(request, will_id):
    will = get_object_or_404(Will, id=will_id)
    generate_will_pdf(will)
    return redirect('will_detail', pk=will.id)



def generate_death_certificate_pdf(dc):
    file_path = os.path.join(settings.MEDIA_ROOT, f"certificates/death_{dc.id}.pdf")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # HEADER
    elements.append(Paragraph("<b>FORM NO.9</b>", styles["Normal"]))
    elements.append(Paragraph("<b>DEATH CERTIFICATE</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "This is to certify that the following information has been taken from official records.",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    #  USE DIRECT FIELDS (NOT WILL)
    elements.append(Paragraph(f"Name: {dc.name}", styles["Normal"]))

    elements.append(Paragraph(f"Aadhaar: {dc.aadhaar}", styles["Normal"]))
    elements.append(Paragraph(f"Father Name: {dc.father_name}", styles["Normal"]))
    elements.append(Paragraph(f"Gender: {dc.gender}", styles["Normal"]))
    
    elements.append(Paragraph(f"Address: {dc.address}", styles["Normal"]))
    elements.append(Paragraph(f"Date of Death: {dc.date_of_death}", styles["Normal"]))
    elements.append(Paragraph(f"Certificate No: {dc.certificate_number}", styles["Normal"]))

    elements.append(Spacer(1, 40))

    elements.append(Paragraph("Signature of Authority", styles["Normal"]))

    doc.build(elements)

    from django.core.files import File
    with open(file_path, "rb") as f:
        dc.certificate_file.save(f"death_{dc.id}.pdf", File(f), save=True)

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Will, DeathCertificate, Testator

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Testator, Will, DeathCertificate
import uuid

def create_death_certificate(request, will_id):
    from .models import Will, DeathCertificate, Testator
    import uuid

    #  ALWAYS GET WILL FIRST (FIX)
    will = Will.objects.get(id=will_id)

    if request.method == "POST":

        aadhaar = request.POST.get("aadhaar")

        #  Find testator
        testator = Testator.objects.filter(aadhaar=aadhaar).first()

        if not testator:
            return HttpResponse("❌ Invalid Aadhaar")

        #  OPTIONAL SAFETY CHECK
        if testator != will.testator:
            return HttpResponse("❌ Aadhaar does not match will")

        #  Create certificate
        dc = DeathCertificate.objects.create(
            will=will,
            aadhaar=aadhaar,
            name=request.POST.get("name"),
            father_name=request.POST.get("father_name"),
            gender=request.POST.get("gender"),
            address=request.POST.get("address"),
            date_of_death=request.POST.get("date_of_death"),
            certificate_number=f"DC-{uuid.uuid4().hex[:8].upper()}",
        )

        generate_death_certificate_pdf(dc)

        return redirect("death_certificate_detail", dc_id=dc.id)

    #  GET request safe now
    return render(request, "dashboard/create_death_certificate.html", {"will": will})
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import DeathCertificate, AssetDistribution
from .blockchain import set_inheritance_on_chain, confirm_death_on_chain
import time


def verify_certificate(request):
    if request.method == "POST":

        aadhaar = request.POST.get("aadhaar").strip()
        dc_id = request.POST.get("dc_id")
        dc_id = request.POST.get("dc_id")

        if dc_id:
            dc = DeathCertificate.objects.get(id=dc_id)
        else:
            # fallback (your current flow)
            dc = DeathCertificate.objects.order_by('-id').first()

        #  Get exact certificate
        

        # Aadhaar check
        if str(dc.aadhaar).strip() != aadhaar:
            return HttpResponse(" Aadhaar mismatch")

        #  File check
        if 'certificate_file' not in request.FILES:
            return HttpResponse("Upload certificate")

        dc.certificate_file = request.FILES['certificate_file']
        dc.status = "VERIFIED"
        dc.save()

        # 🔥 Continue blockchain logic
        will = dc.will

        distributions = AssetDistribution.objects.filter(will=will)

        for d in distributions:
            amount = int(d.asset.value * d.share / 100)

            tx_hash = set_inheritance_on_chain(
                d.beneficiary.wallet_address,
                amount
            )

            d.tx_hash = tx_hash
            d.status = "PROCESSING"
            d.save()

        death_tx = confirm_death_on_chain()

        will.blockchain_tx = death_tx
        will.status = "DECEASED"
        will.save()

        for d in distributions:
            d.tx_hash = death_tx
            d.status = "TRANSFERRED"
            d.save()

        return redirect("beneficiary_dashboard")

    return render(request, "dashboard/upload_certificate.html")

def generate_certificate(request, will_id):
    return redirect("create_death_certificate")
def death_success(request):
    return render(request, "dashboard/death_success.html")
from django.core.files.storage import FileSystemStorage

def upload_certificate(request):
    if request.method == "POST":

        file = request.FILES.get("certificate")

        # ✅ SAFETY CHECK
        if not file:
            return HttpResponse("❌ Please upload certificate file")

        aadhaar = request.POST.get("aadhaar").replace(" ", "").strip()

        from django.core.files.storage import FileSystemStorage
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)

        # get latest certificate (or improve later)
        dc = DeathCertificate.objects.last()

        if not dc:
            return HttpResponse("❌ No certificate found")

        dc_aadhaar = str(dc.aadhaar).replace(" ", "").strip()

        if aadhaar == dc_aadhaar:
            dc.status = "VERIFIED"
            dc.save()
            return HttpResponse("✅ VERIFIED SUCCESSFULLY")

        return HttpResponse("❌ Verification Failed")

    return render(request, "dashboard/upload_certificate.html")
from .blockchain import claim_inheritance_on_chain

from .blockchain import claim_inheritance_on_chain

def claim_asset(request, distribution_id):
    d = AssetDistribution.objects.get(id=distribution_id)

    if request.method == "POST":
        private_key = request.POST.get("private_key")

        tx_hash = claim_inheritance_on_chain(d.will, private_key)

        d.status = "CLAIMED"
        d.tx_hash = tx_hash
        d.save()

        return HttpResponse(f"✅ Claimed: {tx_hash}")

    return render(request, "dashboard/claim.html", {"d": d})
def home(request):
    return render(request, "dashboard/home.html")
def death_certificate_detail(request, dc_id):
    dc = DeathCertificate.objects.get(id=dc_id)

    return render(request, "dashboard/death_certificate_detail.html", {
        "dc": dc
    })
def beneficiary_dashboard(request):
    distributions = AssetDistribution.objects.select_related(
        'beneficiary', 'asset', 'will', 'will__testator'
    )

    return render(request, "dashboard/beneficiary_dashboard.html", {
        "distributions": distributions
    })
def admin_dashboard(request):
    testators = Testator.objects.all()

    return render(request, "dashboard/admin_dashboard.html", {
        "testators": testators
    })
def testator_detail(request, testator_id):
    testator = Testator.objects.get(id=testator_id)

    wills = Will.objects.filter(testator=testator)
    distributions = AssetDistribution.objects.filter(will__testator=testator)

    return render(request, "dashboard/testator_detail.html", {
        "testator": testator,
        "wills": wills,
        "distributions": distributions
    })
    