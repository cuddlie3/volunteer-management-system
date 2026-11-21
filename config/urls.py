from django.contrib import admin
from django.urls import path

from volunteers.views import (
    mini_app,
    applications,
    application_detail,
    approve_application,
    reject_application,
    volunteers,
    volunteer_detail,
    shifts,
    shift_create,
    shift_detail,
    remove_volunteer_from_shift,
    mark_attendance,
    mark_checkout,
    projects,
    zones,
    zone_detail,
    attendance_report,
    hours_report,
    broadcast,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Главная
    path("mini-app/", mini_app, name="mini_app"),

    # Заявки
    path("mini-app/applications/", applications, name="applications"),
    path(
        "mini-app/applications/<int:application_id>/",
        application_detail,
        name="application_detail",
    ),
    path(
        "mini-app/applications/<int:application_id>/approve/",
        approve_application,
        name="approve_application",
    ),
    path(
        "mini-app/applications/<int:application_id>/reject/",
        reject_application,
        name="reject_application",
    ),

    # Волонтёры
    path("mini-app/volunteers/", volunteers, name="volunteers"),
    path(
        "mini-app/volunteers/<int:volunteer_id>/",
        volunteer_detail,
        name="volunteer_detail",
    ),

    # Смены
    path("mini-app/shifts/", shifts, name="shifts"),
    path("mini-app/shifts/create/", shift_create, name="shift_create"),
    path(
        "mini-app/shifts/<int:shift_id>/",
        shift_detail,
        name="shift_detail",
    ),
    path(
        "mini-app/shifts/<int:shift_id>/remove/<int:volunteer_id>/",
        remove_volunteer_from_shift,
        name="remove_volunteer_from_shift",
    ),

    # Посещаемость
    path(
        "mini-app/attendance/<int:assignment_id>/",
        mark_attendance,
        name="mark_attendance",
    ),
    path(
        "mini-app/attendance/<int:assignment_id>/checkout/",
        mark_checkout,
        name="mark_checkout",
    ),
    path(
        "mini-app/attendance/",
        attendance_report,
        name="attendance_report",
    ),

    # Часы
    path(
        "mini-app/hours/",
        hours_report,
        name="hours_report",
    ),

    # Зоны
    path(
        "mini-app/zones/",
        zones,
        name="zones",
    ),
    path(
        "mini-app/zones/<int:zone_id>/",
        zone_detail,
        name="zone_detail",
    ),

    # Рассылка
    path(
        "mini-app/broadcast/",
        broadcast,
        name="broadcast",
    ),

    # Проекты
    path(
        "mini-app/projects/",
        projects,
        name="projects",
    ),
]