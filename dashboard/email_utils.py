from django.core.mail import send_mail

def send_ipfs_email(will, ipfs_hash):
    for b in will.beneficiaries.all():
        send_mail(
            subject="Digital Will Registered",
            message=f"Your will data is stored on IPFS.\nHash: {ipfs_hash}",
            from_email="admin@digitalwill.com",
            recipient_list=[b.address],  # or email field if added
        )
