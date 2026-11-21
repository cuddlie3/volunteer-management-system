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
    list_display = (
        "name",
        "coordinator",
    )

    search_fields = (
        "name",
        "coordinator__username",
    )


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "study_place",
        "telegram_id",
        "created_at",
    )

    search_fields = (
        "full_name",
        "phone",
        "study_place",
        "telegram_id",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "full_name",
    )

    date_hierarchy = "created_at"


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "zone",
        "start_time",
        "end_time",
    )

    list_filter = (
        "zone",
        "start_time",
    )

    search_fields = (
        "name",
        "zone__name",
    )

    ordering = (
        "start_time",
    )


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "volunteer",
        "shift",
        "assigned_at",
    )

    list_filter = (
        "shift",
        "assigned_at",
    )

    search_fields = (
        "volunteer__full_name",
        "shift__name",
    )

    ordering = (
        "-assigned_at",
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "assignment",
        "attended",
        "check_in",
        "check_out",
        "worked_time",
    )

    list_filter = (
        "attended",
    )

    search_fields = (
        "assignment__volunteer__full_name",
    )

    readonly_fields = (
        "worked_time",
    )

    @admin.display(description="Отработано")
    def worked_time(self, obj):
        if obj.check_in and obj.check_out:
            duration = obj.check_out - obj.check_in

            total_seconds = int(duration.total_seconds())

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            return f"{hours} ч {minutes} мин"

        return "—"


@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "study_place",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "full_name",
        "phone",
        "study_place",
        "telegram_id",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        (
            "Личные данные",
            {
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
                )
            },
        ),
        (
            "Рассмотрение заявки",
            {
                "fields": (
                    "status",
                    "created_at",
                )
            },
        ),
    )

    actions = (
        "approve_applications",
        "reject_applications",
    )

    @admin.action(description="Одобрить выбранные заявки")
    def approve_applications(self, request, queryset):
        approved_count = 0

        for application in queryset:
            application.status = VolunteerApplication.STATUS_APPROVED
            application.save()

            Volunteer.objects.get_or_create(
                telegram_id=application.telegram_id,
                defaults={
                    "full_name": application.full_name,
                    "full_name_en": application.full_name_en,
                    "phone": application.phone,
                    "study_place": application.study_place,
                    "address": application.address,
                    "languages": application.languages,
                    "emergency_contact": application.emergency_contact,
                    "id_document_file_id": application.id_document_file_id,
                },
            )

            approved_count += 1

        self.message_user(
            request,
            f"Одобрено заявок: {approved_count}",
        )

    @admin.action(description="Отклонить выбранные заявки")
    def reject_applications(self, request, queryset):
        count = queryset.update(
            status=VolunteerApplication.STATUS_REJECTED
        )

        self.message_user(
            request,
            f"Отклонено заявок: {count}",
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.status != VolunteerApplication.STATUS_APPROVED:
            return

        volunteer_data = {
            "full_name": obj.full_name,
            "full_name_en": obj.full_name_en,
            "phone": obj.phone,
            "study_place": obj.study_place,
            "address": obj.address,
            "languages": obj.languages,
            "emergency_contact": obj.emergency_contact,
            "id_document_file_id": obj.id_document_file_id,
        }

        if obj.telegram_id is not None:
            Volunteer.objects.update_or_create(
                telegram_id=obj.telegram_id,
                defaults=volunteer_data,
            )
        else:
            Volunteer.objects.create(
                **volunteer_data,
            )