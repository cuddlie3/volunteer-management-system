

from django.contrib import admin
from .models import (
    Zone,
    Volunteer,
    Shift,
    Assignment,
    Attendance,
    VolunteerApplication,
)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "coordinator")
    search_fields = ("name",)


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "telegram_id", "created_at")
    search_fields = ("full_name", "phone", "telegram_id")
    list_filter = ("created_at",)
    ordering = ("full_name",)
    date_hierarchy = "created_at"


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "start_time", "end_time")
    list_filter = ("zone", "start_time")
    search_fields = ("name", "zone__name")
    ordering = ("start_time",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("volunteer", "shift", "assigned_at")
    list_filter = ("shift", "assigned_at")
    search_fields = ("volunteer__full_name", "shift__name")
    ordering = ("-assigned_at",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("assignment", "attended", "check_in", "check_out")
    list_filter = ("attended",)
    search_fields = ("assignment__volunteer__full_name",)


@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "phone", "telegram_id")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    fieldsets = (
        ("Личные данные", {
            "fields": (
                "full_name",
                "full_name_en",
                "phone",
                "telegram_id",
                "study_place",
                "address",
                "languages",
                "emergency_contact",
                "id_document_file_id",
            ),
        }),
        ("Рассмотрение заявки", {
            "fields": ("status", "created_at"),
        }),
    )

    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.status != VolunteerApplication.STATUS_APPROVED:
            return

        if obj.telegram_id is not None:
            Volunteer.objects.get_or_create(
                telegram_id=obj.telegram_id,
                defaults={
                    "full_name": obj.full_name,
                    "full_name_en": obj.full_name_en,
                    "phone": obj.phone,
                    "study_place": obj.study_place,
                    "address": obj.address,
                    "languages": obj.languages,
                    "emergency_contact": obj.emergency_contact,
                    "id_document_file_id": obj.id_document_file_id,
                },
            )
        else:
            Volunteer.objects.create(
                full_name=obj.full_name,
                full_name_en=obj.full_name_en,
                phone=obj.phone,
                study_place=obj.study_place,
                address=obj.address,
                languages=obj.languages,
                emergency_contact=obj.emergency_contact,
                id_document_file_id=obj.id_document_file_id,
            )


        super().save_model(request, obj, form, change)
