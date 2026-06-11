from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Will


@receiver(post_save, sender=Will)
def automate_will_processing(sender, instance, created, **kwargs):

    # 🔒 Only run when status becomes ACTIVE
    if instance.status != Will.Status.ACTIVE:
        return

    # 🔒 Prevent recursion: only run if not already processed
    if instance.ipfs_hash:
        return

    # ---------------------------------
    # 1️⃣ Generate PDF
    # ---------------------------------
    from .utils.pdf_generator import generate_will_pdf
    pdf_relative_path = generate_will_pdf(instance)

    # ⚠ IMPORTANT: use update() instead of save()
    Will.objects.filter(pk=instance.pk).update(
        will_document=pdf_relative_path
    )

    # ---------------------------------
    # 2️⃣ Upload to IPFS
    # ---------------------------------
    from .ipfs import upload_to_ipfs
    full_path = instance.will_document.field.storage.path(pdf_relative_path)
    ipfs_hash = upload_to_ipfs(full_path)

    # ---------------------------------
    # 3️⃣ PQ Sign
    # ---------------------------------
    from .utils.pqcrypto_utils import pq_sign_data

    with open(full_path, "rb") as f:
        file_bytes = f.read()

    signature, public_key = pq_sign_data(file_bytes)

    # ---------------------------------
    # 4️⃣ Final Update (NO save())
    # ---------------------------------
    Will.objects.filter(pk=instance.pk).update(
        ipfs_hash=ipfs_hash,
        pq_signature=signature,
        pq_public_key=public_key
    )