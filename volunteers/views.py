from datetime import datetime, timedelta
import asyncio
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    VolunteerApplication,
    Volunteer,
    Shift,
    Zone,
    Assignment,
    Attendance,
)


def mini_app(request):
    volunteers_count = Volunteer.objects.count()
    applications_count = VolunteerApplication.objects.count()
    shifts_count = Shift.objects.count()
    zones_count = Zone.objects.count()
    assignments_count = Assignment.objects.count()
    attended_count = Attendance.objects.filter(attended=True).count()

    total_work_time = timedelta()

    attendances = Attendance.objects.filter(
        check_in__isnull=False,
        check_out__isnull=False,
    )

    for attendance in attendances:
        total_work_time += (
            attendance.check_out - attendance.check_in
        )

    total_hours = total_work_time.days * 24 + (
        total_work_time.seconds // 3600
    )

    total_minutes = (
        total_work_time.seconds % 3600
    ) // 60

    return render(
        request,
        "volunteers/mini_app.html",
        {
            "volunteers_count": volunteers_count,
            "applications_count": applications_count,
            "shifts_count": shifts_count,
            "zones_count": zones_count,
            "assignments_count": assignments_count,
            "attended_count": attended_count,
            "total_hours": total_hours,
            "total_minutes": total_minutes,
        },
    )   

def applications(request):
    applications = VolunteerApplication.objects.all().order_by("-created_at")

    return render(
        request,
        "volunteers/applications.html",
        {
            "applications": applications,
        },
    )


def application_detail(request, application_id):
    application = get_object_or_404(
        VolunteerApplication,
        id=application_id,
    )

    return render(
        request,
        "volunteers/application_detail.html",
        {
            "application": application,
        },
    )


def approve_application(request, application_id):
    if request.method == "POST":
        application = get_object_or_404(
            VolunteerApplication,
            id=application_id,
        )

        application.status = VolunteerApplication.STATUS_APPROVED
        application.save()

        volunteer_data = {
            "full_name": application.full_name,
            "full_name_en": application.full_name_en,
            "phone": application.phone,
            "study_place": application.study_place,
            "address": application.address,
            "languages": application.languages,
            "emergency_contact": application.emergency_contact,
            "id_document_file_id": application.id_document_file_id,
        }

        if application.telegram_id:
            Volunteer.objects.update_or_create(
                telegram_id=application.telegram_id,
                defaults=volunteer_data,
            )
        else:
            Volunteer.objects.create(
                **volunteer_data
            )

    return redirect("/mini-app/applications/")


def reject_application(request, application_id):
    if request.method == "POST":
        application = get_object_or_404(
            VolunteerApplication,
            id=application_id,
        )

        application.status = VolunteerApplication.STATUS_REJECTED
        application.save()

    return redirect("/mini-app/applications/")


def volunteers(request):
    query = request.GET.get("q", "").strip()
    zone_id = request.GET.get("zone", "").strip()

    volunteers = Volunteer.objects.all().order_by("full_name")
    zones = Zone.objects.all().order_by("name")

    if query:
        volunteers = volunteers.filter(
            full_name__icontains=query
        ) | volunteers.filter(
            phone__icontains=query
        )

    if zone_id:
        volunteers = volunteers.filter(
            assignments__shift__zone_id=zone_id
        ).distinct()

    return render(
        request,
        "volunteers/volunteers.html",
        {
            "volunteers": volunteers,
            "zones": zones,
            "query": query,
            "selected_zone": zone_id,
        },
    )


def volunteer_detail(request, volunteer_id):
    volunteer = get_object_or_404(
        Volunteer,
        id=volunteer_id,
    )

    assignments = Assignment.objects.filter(
        volunteer=volunteer
    ).select_related(
        "shift",
        "shift__zone",
        "attendance",
    ).order_by(
        "-shift__start_time"
    )

    total_shifts = assignments.count()
    attended_shifts = 0
    total_work_time = timedelta()

    for assignment in assignments:
        attendance = getattr(assignment, "attendance", None)

        if attendance and attendance.attended:
            attended_shifts += 1

        if (
            attendance
            and attendance.check_in
            and attendance.check_out
        ):
            total_work_time += (
                attendance.check_out - attendance.check_in
            )

    total_hours = total_work_time.days * 24 + (
        total_work_time.seconds // 3600
    )

    total_minutes = (
        total_work_time.seconds % 3600
    ) // 60

    return render(
        request,
        "volunteers/volunteer_detail.html",
        {
            "volunteer": volunteer,
            "assignments": assignments,
            "total_shifts": total_shifts,
            "attended_shifts": attended_shifts,
            "total_hours": total_hours,
            "total_minutes": total_minutes,
        },
    )


def shifts(request):
    today = datetime.now()

    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    # Нормализуем месяц
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    first_day = datetime(year, month, 1)

    if month == 12:
        next_month_date = datetime(year + 1, 1, 1)
    else:
        next_month_date = datetime(year, month + 1, 1)

    previous_month_date = (
        datetime(year - 1, 12, 1)
        if month == 1
        else datetime(year, month - 1, 1)
    )

    days_in_month = (next_month_date - first_day).days

    shifts = Shift.objects.select_related("zone").filter(
        start_time__year=year,
        start_time__month=month,
    ).order_by("start_time")

    # Группируем смены по дню
    shifts_by_day = {}

    for shift in shifts:
        day = shift.start_time.day
        shifts_by_day.setdefault(day, []).append(shift)

    # Понедельник = 0, воскресенье = 6
    first_weekday = first_day.weekday()

    calendar_rows = []

    current_day = 1

    # Первая неделя
    week = [None] * first_weekday

    while len(week) < 7 and current_day <= days_in_month:
        week.append(current_day)
        current_day += 1

    calendar_rows.append(week)

    # Остальные недели
    while current_day <= days_in_month:
        week = []

        for _ in range(7):
            if current_day <= days_in_month:
                week.append(current_day)
                current_day += 1
            else:
                week.append(None)

        calendar_rows.append(week)

    month_names = [
        "",
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]

    return render(
        request,
        "volunteers/shifts.html",
        {
            "shifts": shifts,
            "calendar_rows": calendar_rows,
            "shifts_by_day": shifts_by_day,
            "selected_month": month,
            "selected_year": year,
            "month_label": f"{month_names[month]} {year}",
            "previous_month": previous_month_date,
            "next_month": next_month_date,
        },
    )


def shift_create(request):
    zones = Zone.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        zone_id = request.POST.get("zone")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        description = request.POST.get("description")

        if start_time:
            start_time = datetime.fromisoformat(start_time)

        if end_time:
            end_time = datetime.fromisoformat(end_time)

        Shift.objects.create(
            name=name,
            zone_id=zone_id,
            start_time=start_time,
            end_time=end_time,
            description=description,
        )

        return redirect("/mini-app/shifts/")

    return render(
        request,
        "volunteers/shift_create.html",
        {
            "zones": zones,
        },
    )


def shift_detail(request, shift_id):
    shift = get_object_or_404(
        Shift.objects.select_related("zone"),
        id=shift_id,
    )

    volunteers = Volunteer.objects.all().order_by("full_name")

    assigned_volunteers = Volunteer.objects.filter(
        assignments__shift=shift
    ).prefetch_related(
        "assignments__attendance"
    ).order_by("full_name")

    if request.method == "POST":

        # Добавление волонтёра на смену
        if request.POST.get("action") == "assign":
            volunteer_id = request.POST.get("volunteer_id")

            volunteer = get_object_or_404(
                Volunteer,
                id=volunteer_id,
            )

            assignment, created = Assignment.objects.get_or_create(
                volunteer=volunteer,
                shift=shift,
            )

            Attendance.objects.get_or_create(
                assignment=assignment
            )

            return redirect(f"/mini-app/shifts/{shift_id}/")

        # Сохранение заметки координатора
        if request.POST.get("action") == "note":
            shift.description = request.POST.get(
                "description",
                ""
            ).strip()

            shift.save(update_fields=["description"])

            return redirect(f"/mini-app/shifts/{shift_id}/")

    return render(
        request,
        "volunteers/shift_detail.html",
        {
            "shift": shift,
            "volunteers": volunteers,
            "assigned_volunteers": assigned_volunteers,
        },
    )

def remove_volunteer_from_shift(request, shift_id, volunteer_id):
    if request.method == "POST":
        assignment = get_object_or_404(
            Assignment,
            shift_id=shift_id,
            volunteer_id=volunteer_id,
        )

        assignment.delete()

    return redirect(f"/mini-app/shifts/{shift_id}/")


def mark_attendance(request, assignment_id):
    if request.method == "POST":
        assignment = get_object_or_404(
            Assignment,
            id=assignment_id,
        )

        attendance, created = Attendance.objects.get_or_create(
            assignment=assignment
        )

        attendance.attended = True
        attendance.check_in = datetime.now()
        attendance.save()

    return redirect(
        f"/mini-app/shifts/{assignment.shift_id}/"
    )


def mark_checkout(request, assignment_id):
    if request.method == "POST":
        assignment = get_object_or_404(
            Assignment,
            id=assignment_id,
        )

        attendance = get_object_or_404(
            Attendance,
            assignment=assignment,
        )

        attendance.check_out = datetime.now()
        attendance.save()

    return redirect(
        f"/mini-app/shifts/{assignment.shift_id}/"
    )
def projects(request):
    return render(
        request,
        "volunteers/projects.html",
    )

    from django.db.models import Count, Q


def zones(request):
    zones_qs = (
        Zone.objects
        .select_related("coordinator")
        .prefetch_related("shifts")
    )

    for zone in zones_qs:
        zone.shifts_count = zone.shifts.count()

        zone.volunteers_count = Volunteer.objects.filter(
            assignments__shift__zone=zone
        ).distinct().count()

    return render(
        request,
        "volunteers/zones.html",
        {
            "zones": zones_qs,
        },
    )


def zone_detail(request, zone_id):
    zone = get_object_or_404(Zone, id=zone_id)

    zone_shifts = Shift.objects.filter(
        zone=zone
    ).order_by("start_time")

    zone_volunteers = Volunteer.objects.filter(
        assignments__shift__zone=zone
    ).distinct().order_by("full_name")

    return render(
        request,
        "volunteers/zone_detail.html",
        {
            "zone": zone,
            "zone_shifts": zone_shifts,
            "zone_volunteers": zone_volunteers,
        },
    )
def attendance_report(request):
    attendances = Attendance.objects.select_related(
        "assignment__volunteer",
        "assignment__shift",
        "assignment__shift__zone",
    ).order_by(
        "-assignment__shift__start_time"
    )

    status = request.GET.get("status", "")

    if status == "present":
        attendances = attendances.filter(attended=True)

    elif status == "absent":
        attendances = attendances.filter(attended=False)

    return render(
        request,
        "volunteers/attendance.html",
        {
            "attendances": attendances,
            "status": status,
        },
    )    

def hours_report(request):
    assignments = Assignment.objects.select_related(
        "volunteer",
        "shift",
        "shift__zone",
        "attendance",
    ).order_by(
        "volunteer__full_name",
        "shift__start_time",
    )

    volunteer_hours = {}

    for assignment in assignments:
        attendance = getattr(
            assignment,
            "attendance",
            None,
        )

        if (
            attendance
            and attendance.check_in
            and attendance.check_out
        ):
            work_time = (
                attendance.check_out
                - attendance.check_in
            )

            if assignment.volunteer_id not in volunteer_hours:
                volunteer_hours[assignment.volunteer_id] = {
                    "volunteer": assignment.volunteer,
                    "total": timedelta(),
                }

            volunteer_hours[
                assignment.volunteer_id
            ]["total"] += work_time

    for item in volunteer_hours.values():
        total = item["total"]

        item["hours"] = (
            total.days * 24
            + total.seconds // 3600
        )

        item["minutes"] = (
            total.seconds % 3600
        ) // 60

    return render(
        request,
        "volunteers/hours.html",
        {
            "volunteer_hours": volunteer_hours.values(),
        },
    )

def broadcast(request):
    from django.contrib import messages
    from .models import Shift, Volunteer

    shifts_qs = Shift.objects.select_related("zone").order_by("-start_time")

    if request.method == "POST":
        shift_id = request.POST.get("shift_id")
        message_text = request.POST.get("message", "").strip()

        if not shift_id or not message_text:
            messages.error(request, "Выберите смену и введите сообщение.")
            return render(
                request,
                "volunteers/broadcast.html",
                {"shifts": shifts_qs},
            )

        shift = get_object_or_404(Shift, id=shift_id)

        recipients = list(
            Volunteer.objects.filter(
                assignments__shift=shift,
                telegram_id__isnull=False,
            )
            .values_list("telegram_id", flat=True)
            .distinct()
        )

        if not recipients:
            messages.warning(
                request,
                "У этой смены нет назначенных волонтёров с Telegram ID.",
            )
            return render(
                request,
                "volunteers/broadcast.html",
                {"shifts": shifts_qs},
            )

        try:
            from .telegram_utils import broadcast_message

            sent, failed = asyncio.run(
                broadcast_message(
                    recipients,
                    message_text,
                )
            )

            messages.success(
                request,
                f"Отправлено: {sent}. Ошибок: {failed}.",
            )

        except Exception as exc:
            messages.error(
                request,
                f"Не удалось выполнить рассылку: {exc}",
            )

    return render(
        request,
        "volunteers/broadcast.html",
        {"shifts": shifts_qs},
    )