from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # homepage

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('testator/<int:testator_id>/', views.testator_detail, name='testator_detail'),

    path('beneficiary-dashboard/', views.beneficiary_dashboard, name='beneficiary_dashboard'),

    path("claim/<int:will_id>/", views.claim_inheritance, name="claim_inheritance"),

    path("activate/<int:will_id>/", views.activate_will, name="activate_will"),
    


    path("create-will/", views.create_will, name="create_will"),

    path("will/<int:pk>/", views.will_detail, name="will_detail"),

    path("will/<int:pk>/add-distribution/", views.add_distribution, name="add_distribution"),

    # ✅ NEW (IMPORTANT)
    path("generate-pdf/<int:will_id>/", views.generate_will_pdf_view, name="generate_pdf"),

    path("generate-certificate/<int:will_id>/", views.generate_certificate, name="generate_certificate"),
    path('create-death-certificate/<int:will_id>/', views.create_death_certificate, name='create_death_certificate'),
    path("verify/<int:dc_id>/", views.verify_certificate, name="verify_certificate"),

path("death-success/", views.death_success, name="death_success"),
path('upload-certificate/', views.verify_certificate, name='upload_certificate'),
path("claim/<int:distribution_id>/", views.claim_asset, name="claim_asset"),
path('verify-certificate/', views.verify_certificate, name='verify_certificate'),
path("death-certificate/<int:dc_id>/", views.death_certificate_detail, name="death_certificate_detail"),

]