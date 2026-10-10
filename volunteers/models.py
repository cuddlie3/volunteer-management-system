
from django.conf import settings
from django.db import models


class Zone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="coordinated_zones",
    )

    class Meta:
        verbose_name = "Зона"
        verbose_name_plural = "Зоны"

    def __str__(self):
        return self.name


class Volunteer(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="ФИО")

    full_name_en = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="ФИО на английском",
    )
    study_place = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Место учёбы",
    )
    address = models.TextField(
        blank=True,
        verbose_name="Домашний адрес",
    )
    languages = models.TextField(
        blank=True,
        verbose_name="Языки",
    )
    emergency_contact = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Экстренный контакт",
    )
    id_document_file_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Идентификатор документа в Telegram",
    )

    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="Telegram ID",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации",
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Волонтёр"
        verbose_name_plural = "Волонтёры"


class Shift(models.Model):
    zone = models.ForeignKey(
        Zone,
        on_delete=models.PROTECT,
        related_name="shifts",
        verbose_name="Зона",
    )
    name = models.CharField(max_length=150, verbose_name="Название смены")
    start_time = models.DateTimeField(verbose_name="Начало смены")
    end_time = models.DateTimeField(verbose_name="Окончание смены")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return f"{self.name} — {self.zone.name}"

    class Meta:
        verbose_name = "Смена"
        verbose_name_plural = "Смены"
        ordering = ("start_time",)


class Assignment(models.Model):
    volunteer = models.ForeignKey(
        Volunteer,
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name="Волонтёр",
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name="Смена",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата назначения",
    )

    def __str__(self):
        return f"{self.volunteer.full_name} — {self.shift.name}"

    class Meta:
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"
        constraints = [
            models.UniqueConstraint(
                fields=("volunteer", "shift"),
                name="unique_volunteer_shift",
            )
        ]


class Attendance(models.Model):
    assignment = models.OneToOneField(
        Assignment,
        on_delete=models.PROTECT,
        related_name="attendance",
        verbose_name="Назначение",
    )
    attended = models.BooleanField(
        default=False,
        verbose_name="Присутствовал",
    )
    check_in = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время прихода",
    )
    check_out = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время ухода",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Примечания",
    )

    def __str__(self):
        return f"Посещаемость: {self.assignment}"

    class Meta:
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемость"


class VolunteerApplication(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает подтверждения"),
        (STATUS_APPROVED, "Одобрена"),
        (STATUS_REJECTED, "Отклонена"),
    ]

    full_name = models.CharField(
        max_length=150,
        verbose_name="ФИО",
    )
    full_name_en = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="ФИО на английском",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
    )
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Telegram ID",
    )
    study_place = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Место учёбы",
    )
    address = models.TextField(
        blank=True,
        verbose_name="Домашний адрес",
    )
    languages = models.TextField(
        blank=True,
        verbose_name="Языки",
    )
    emergency_contact = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Экстренный контакт",
    )
    id_document_file_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Идентификатор документа в Telegram",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Статус заявки",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подачи заявки",
    )

    def __str__(self):
        return f"{self.full_name} — {self.get_status_display()}"

    class Meta:
        verbose_name = "Заявка волонтёра"
        verbose_name_plural = "Заявки волонтёров"
        ordering = ("-created_at",)
