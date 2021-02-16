import pytz
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
import datetime


class Alias(models.Model):
    alias = models.CharField(max_length=120)
    target = models.SlugField(max_length=24)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)

    def _alias_params_check(self):
        """Check correct input of start and end values."""

        try:
            if self.start > self.end:
                raise ValidationError('Alias can not end before start!')
        except TypeError:
            pass

        return True

    @staticmethod
    def _add_timezone(*args):
        """Add timezone to datetime type values if needed."""
        for value in args:
            if not value.tzname():
                return pytz.utc.localize(value)
            return value

    @staticmethod
    def _get_pre_aliases(target: str or models.SlugField, alias=None):
        """Return aliases by alias and target values."""
        if not alias:
            return Alias.objects.filter(target=target)
        return Alias.objects.filter(alias=alias, target=target)

    def _overlap_check(self):
        """Check new instance for overlapping with existing ones."""
        data = self._get_pre_aliases(alias=self.alias, target=self.target).exclude(id=self.pk)

        # For creating of finite alias.
        if self.end:
            # Compare with finite and infinite aliases.
            if data.filter(Q(start__lt=self.end) & (Q(end__gt=self.start) | Q(end__isnull=True))):
                raise ValidationError('Aliases can not overlap!')

        # For creating of infinite alias.
        if not self.end:
            # Compare with finite aliases.
            if data.filter(end__gt=self.start):
                raise ValidationError('Aliases can not overlap!')
            # Compare with infinite aliases.
            if data.filter(end=None):
                raise ValidationError('Aliases can not overlap!')

        return True

    @staticmethod
    def get_aliases(target: str, from_: datetime, to: datetime):
        """
        Return set of aliases.

        Keyword arguments:
            target -- the object to which alias refer.
            from_ -- the starting point of time range.
            to -- the ending point of time range.

        Return:
            the set of aliases in the specified time range.
        """

        # Add a timezone to time var.
        try:
            from_ = Alias._add_timezone(from_)
            to = Alias._add_timezone(to)
        except ValueError:
            pass

        if from_ > to:
            raise ValidationError('Time range can not end before start!')

        data = Alias._get_pre_aliases(target=target)
        # QuerySet of aliases in the specified time range.

        data = data.filter((Q(start__lt=to) & (Q(end__gt=from_) | Q(end__isnull=True))))
        aliases = set(item.alias for item in data)

        return aliases

    @staticmethod
    def alias_replace(existing_alias: str, replace_at: datetime, new_alias_value: str):
        """
        Replace existing alias with a new one.

        Keyword arguments:
            existing_alias -- alias value of the existing Alias instance.
            replace_at -- a moment of time.
            new_alias_value -- alias value of the new Alias instance.

        Return:
            set alias.end = replace_at for existing_alias. Creates new alias
            with alias value = new_alias_value, start = replace_at, end = None.
        """
        # Check for new alias value.
        if existing_alias == new_alias_value:
            raise ValidationError('You can not replace alias with the same alias value!')
        # Add a timezone to time replace_at.

        try:
            replace_at = Alias._add_timezone(replace_at)
        except ValueError:
            pass

        # Process no alias to replace.
        try:
            alias = Alias.objects.get(alias=existing_alias, start__lte=replace_at, end__gt=replace_at)
        except models.ObjectDoesNotExist:
            raise ValidationError('Alias does not exist!')
        alias.end = replace_at
        alias.save()
        Alias.objects.create(alias=new_alias_value, target=alias.target, start=replace_at, end=None)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Save alias."""

        # Check parameters correct input.
        if self._alias_params_check():
            # Check for overlapping.
            if self._overlap_check():
                super(Alias, self).save()
