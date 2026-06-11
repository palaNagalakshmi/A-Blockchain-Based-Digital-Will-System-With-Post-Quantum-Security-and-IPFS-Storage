from django.db import models


# ============================
# TESTATOR
# ============================
from django.core.validators import RegexValidator

aadhaar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message="Aadhaar must be exactly 12 digits"
)


class Testator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    aadhaar = models.CharField(
        max_length=12,
        unique=True,
        validators=[aadhaar_validator]
    )

    # 🔥 ADD THIS
    wallet_address = models.CharField(
    max_length=42,
    default="0x0000000000000000000000000000000000000000"
)

    def __str__(self):
        return self.name
# ============================
# BENEFICIARY
# ============================
class Beneficiary(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    # 🔥 ADD THIS
    wallet_address = models.CharField(
    max_length=42,
    default="0x0000000000000000000000000000000000000000"
)
    private_key = models.CharField(max_length=100, null=True, blank=True)
    

    def __str__(self):
        return self.name

# ============================
# ASSET
# ============================
class Asset(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField()
    owner = models.ForeignKey(Testator, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# ============================
# WILL
# ============================
class Will(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        DECEASED = "DECEASED", "Deceased"
        COMPLETED = "COMPLETED", "Completed"

    testator = models.ForeignKey(Testator, on_delete=models.CASCADE)

    beneficiaries = models.ManyToManyField(Beneficiary)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    will_document = models.FileField(
        upload_to="wills/",
        null=True,
        blank=True
    )

    blockchain_tx = models.CharField(max_length=255, blank=True, null=True)
    ipfs_hash = models.CharField(max_length=255, blank=True, null=True)
    pq_signature = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Will {self.id} - {self.testator.name}"


# ============================
# ASSET DISTRIBUTION
# ============================
class AssetDistribution(models.Model):
    will = models.ForeignKey(Will, on_delete=models.CASCADE)

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    share = models.FloatField()

    # ✅ ADD THESE TWO LINES
    tx_hash = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default="PENDING")

    def __str__(self):
        return f"{self.asset.name} → {self.beneficiary.name}"

certificate_file = models.FileField(upload_to="certificates/", null=True, blank=True)
# ============================
# DEATH CERTIFICATE
# ============================
class DeathCertificate(models.Model):
    will = models.ForeignKey(Will, on_delete=models.CASCADE, null=True, blank=True)
    
    certificate_number = models.CharField(max_length=50)
    name = models.CharField(max_length=100, null=True, blank=True)
    aadhaar = models.CharField(max_length=12)   # ✅ REQUIRED

    date_of_death = models.CharField(max_length=20)
    
    father_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_registration = models.CharField(max_length=20, null=True, blank=True)

    certificate_file = models.FileField(upload_to="certificates/", null=True, blank=True)

    status = models.CharField(max_length=20, default="PENDING")  # VERIFIED / PENDING
    