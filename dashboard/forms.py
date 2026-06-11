from django import forms
from .models import Will, AssetDistribution, Asset, DeathCertificate


# ================= WILL FORM =================
class WillForm(forms.ModelForm):

    class Meta:
        model = Will
        fields = ["testator", "beneficiaries"]


# ================= DISTRIBUTION FORM =================
class AssetDistributionForm(forms.ModelForm):

    class Meta:
        model = AssetDistribution
        fields = ["asset", "beneficiary", "share_percentage"]

    def __init__(self, *args, **kwargs):
        will = kwargs.pop("will", None)
        super().__init__(*args, **kwargs)

        if will:
            # Show only assets of selected testator
            self.fields["asset"].queryset = Asset.objects.filter(
                owner=will.testator
            )

            # Show only beneficiaries of this will
            self.fields["beneficiary"].queryset = will.beneficiaries.all()


# ================= DEATH CERTIFICATE FORM =================
class DeathCertificateForm(forms.ModelForm):

    certificate_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter Certificate Number",
            "style": "width:100%; padding:8px;"
        })
    )

    aadhaar = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "XXXX XXXX XXXX",
            "style": "width:100%; padding:8px;",
            "maxlength": "14"
        })
    )

    class Meta:
        model = DeathCertificate   # 🔥 VERY IMPORTANT
        fields = ["will", "certificate_number", "aadhaar"]

    def clean_aadhaar(self):
        aadhaar = self.cleaned_data.get("aadhaar", "").replace(" ", "")

        if len(aadhaar) != 12 or not aadhaar.isdigit():
            raise forms.ValidationError("Enter valid 12-digit Aadhaar number")

        return aadhaar