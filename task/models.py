import enum
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from partner.models import Partner


logger = logging.getLogger(__name__)

number_tr = _("number")

# Fields used to create an index in the DB and sort the tasks in the Admin
TASK_PRIORITY_FIELDS = ('state', '-priority', '-deadline')


class State(enum.Enum):
    """
    Status of completion of the task
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    TO_DO = '00-to-do'
    IN_PROGRESS = '10-in-progress'
    BLOCKED = '20-blocked'
    DONE = '30-done'
    DISMISSED = '40-dismissed'


class Priority(enum.Enum):
    """
    The priority of the task
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    LOW = '00-low'
    NORMAL = '10-normal'
    HIGH = '20-high'
    CRITICAL = '30-critical'


class TaskManager(models.Manager):

    def others(self, pk, **kwargs):
        """
        Return queryset with all objects
        excluding the one with the "pk" passed, but
        applying the filters passed in "kwargs".
        """
        return self.exclude(pk=pk).filter(**kwargs)


class Task(models.Model):
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    STATES = (
        (State.TO_DO.value, _('To Do')),
        (State.IN_PROGRESS.value, _('In Progress')),
        (State.BLOCKED.value, _('Blocked')),
        (State.DONE.value, _('Done')),
        (State.DISMISSED.value, _('Dismissed'))
    )

    PRIORITIES = (
        (Priority.LOW.value, _('Low')),
        (Priority.NORMAL.value, _('Normal')),
        (Priority.HIGH.value, _('High')),
        (Priority.CRITICAL.value, _('Critical')),
    )

    title = models.CharField(_("title"), max_length=200)
    partner = models.ForeignKey(Partner, blank=True, null=True, on_delete=models.PROTECT)
    description = models.TextField(_("description"), max_length=2000, null=True, blank=True)
    resolution = models.TextField(_("resolution"), max_length=2000, null=True, blank=True)
    deadline = models.DateField(_("deadline"), null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tasks_assigned', verbose_name=_('assigned to'),
                             on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(_("state"), max_length=20, choices=STATES, default=State.TO_DO.value)
    priority = models.CharField(_("priority"), max_length=20, choices=PRIORITIES, default=Priority.NORMAL.value)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='users_created', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

    objects = TaskManager()

    class Meta:
        indexes = [
            models.Index(fields=TASK_PRIORITY_FIELDS, name='mtasks_task_priority_idx'),
        ]

    def __str__(self):
        return "[%s] %s" % (self.number, self.title)

    @property
    def number(self) -> str:
        return "{:08d}".format(self.pk)

    def clean(self):
        validation_errors = {}
        title = self.title.strip() if self.title else self.title
        if self.partner:
            if Task.objects \
                    .others(self.pk, title=title, partner=self.partner) \
                    .exclude(state__in=(State.DONE.value, State.DISMISSED.value)) \
                    .exists():
                validation_errors['title'] = _('Open task with this title and partner already exists.')
        else:
            if Task.objects \
                    .others(self.pk, title=title, partner=None) \
                    .exclude(state__in=(State.DONE.value, State.DISMISSED.value)) \
                    .exists():
                validation_errors['title'] = _('Open task with this title and no partner already exists.')

        # Add more validations HERE

        if len(validation_errors):
            raise ValidationError(validation_errors)


class Item(models.Model):
    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Check List")

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    item_description = models.CharField(_("description"), max_length=200)
    is_done = models.BooleanField(_("done?"), default=False)

    def __str__(self):
        return self.item_description