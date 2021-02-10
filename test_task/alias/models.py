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

    def _overlap_check(self):
        """Check new instance for overlapping with existing ones."""

        data = Alias.objects.filter(alias=self.alias, target=self.target).exclude(id=self.pk)
        # For creating of finite alias.
        if self.end:
            # compare with finite aliases.
            if data.filter(Q(start__lt=self.end, end__gt=self.end) | Q(start__lt=self.end, end__gt=self.start) |
                           Q(start__lte=self.start, end__gte=self.end)):
                raise ValidationError('Aliases can not overlap!')
            # Compare with infinite aliases.
            if data.filter(start__lt=self.end, end=None):
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
            from_ = pytz.utc.localize(from_)
            to = pytz.utc.localize(to)
        except ValueError:
            pass

        if from_ > to:
            raise ValidationError('Alias can not end before start!')

        # QuerySet of aliases in the specified time range.
        data = Alias.objects.filter(
            (
                (Q(target=target, start__range=[from_, to])) |
                (Q(target=target, end__range=[from_, to]) & ~Q(end=from_)) |
                (Q(target=target, start__lt=from_, end__gt=to)) |
                (Q(target=target, start__lte=to, end=None))
             )
        )

        aliases = [item.alias for item in data]

        return set(aliases)

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
            replace_at = pytz.utc.localize(replace_at)
        except ValueError:
            pass

        # Process no alias to replace.
        try:
            alias = Alias.objects.filter(alias=existing_alias, start__lte=replace_at).exclude(end__lt=replace_at)[0]
        except IndexError:
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
