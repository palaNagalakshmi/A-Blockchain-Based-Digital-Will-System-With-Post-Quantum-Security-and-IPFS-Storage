from dashboard.models import DeathCertificate
from dashboard.blockchain import confirm_death_on_chain


def verify_death_certificate(will_id):
    dc = DeathCertificate.objects.get(will_id=will_id)

    dc.verify()

    will = dc.will
    will.status = will.Status.DECEASED
    will.save()

    # ✅ pass will correctly
    confirm_death_on_chain(will)

    return True