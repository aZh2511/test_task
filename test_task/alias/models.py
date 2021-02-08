import pytz
from django.core.exceptions import ValidationError
from django.db import models


class Alias(models.Model):
    alias = models.CharField(max_length=120)
    target = models.SlugField(max_length=24)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)

    def _alias_params_check(self, data):
        """
        Alias method that checks adherence of Alias instance for following conditions:
            1. Checks correct start - ebd input (start < end).
            2. Checks for uniqueness of alias target. Aliases with same alias value can not refer to different targets.

        :param data: QuerySet of aliases
        :return: True if conditions are followed, otherwise raises a ValidationError
        """
        # 1
        try:
            if self.start > self.end:
                raise ValidationError('Alias can not end before start!')
        except TypeError:
            pass

        # 2
        for item in data:
            if self.target != item.target:
                raise ValidationError(f'Aliases with same alias value must refer to the same target! '
                                      f'Alias "{item.alias}" already refers to "{item.target}" target.')
        return True

    def _overlap_check(self, data):
        """
        Alias method that checks new alias initialization for overlapping with existing ones.

        :param data: QuerySet of aliases
        :return: True if conditions are followed, otherwise raises a ValidationError
        """
        for item in data:
            if self.pk != item.pk:      # Replacing values, current alias will be compared with itself - avoid that
                # For two finite gaps
                if all((item.end, self.end)):
                    # Starting point inside of existing gap
                    if item.start <= self.start < item.end:
                        raise ValidationError('Aliases can not overlap!')
                    # Ending point inside of existing gap
                    elif item.start < self.end < item.end:
                        raise ValidationError('Aliases can not overlap!')
                    # New gap covers existing one
                    elif (self.start < item.start) and (self.end > item.end):
                        raise ValidationError('Aliases can not overlap!')

                # For infinite and finite gaps
                elif self.end or item.end:
                    # Creating of finite gap
                    if self.end:
                        if not (self.end <= item.start):
                            raise ValidationError('Aliases can not overlap!')
                    # Creating of infinite gap
                    else:
                        if not (self.start >= item.end):
                            raise ValidationError('Aliases can not overlap!')

                # Two infinite gaps
                else:
                    raise ValidationError('Aliases can not overlap!')

        return True

    @staticmethod
    def get_aliases(target: str, from_, to):
        """
        Alias method that returns set of aliases.

        :param target: object to which aliases refer (lead to)
        :param from_: starting point of time range in which we want to get aliases
        :param to: ending point of time range in which we want to get aliases
        :return: set of aliases that fit the conditions
        """
        # Add a timezone to time var. Pass if already set
        try:
            from_ = pytz.utc.localize(from_)
            to = pytz.utc.localize(to)
        except ValueError:
            pass

        if from_ > to:
            raise ValidationError('Alias can not end before start!')

        # Aliases on the left of time range
        data = Alias.objects.filter(target=target, start__lte=from_).exclude(end__lt=from_)
        aliases = [item.alias for item in data]
        # Aliases on the right of time range
        data = Alias.objects.filter(target=target, end__gte=to).exclude(start__gt=to)
        for item in data:
            aliases.append(item.alias)

        return set(aliases)

    @staticmethod
    def alias_replace(existing_alias: str, replace_at, new_alias_value: str):
        """
        Alias method that replace an existing alias with a new one.

        :param existing_alias: alias value of Alias instance, which we want to replace
        :param replace_at: moment of time at which we want to replace. Will be set as end value for the Alias with alias
        value == existing_alias and start value for the Alias with alias value == new_alias_value
        :param new_alias_value: alias value of an Alias object we create
        :return: nothing. Creates an instance of Alias class due to given params
        """
        # Check for new alias value
        if existing_alias == new_alias_value:
            raise ValidationError('You can not replace alias with the same alias value!')
        # Add a timezone to time var. Pass if already set
        try:
            replace_at = pytz.utc.localize(replace_at)
        except ValueError:
            pass

        # Check for no matches
        try:
            alias = Alias.objects.filter(alias=existing_alias, start__lte=replace_at).exclude(end__lt=replace_at)[0]
        except IndexError:     # Provide a certain mistake? IndexError and empty Query mistakes only
            raise ValidationError('Alias does not exist!')
        alias.end = replace_at
        alias.save()
        Alias.objects.create(alias=new_alias_value, target=alias.target, start=replace_at, end=None)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Modified special Alias save method to avoid incorrect aliases criteria input.

        :return: save() for appropriate instances
        """

        data = Alias.objects.filter(alias=self.alias)

        # Validation check for alias target
        if self._alias_params_check(data):
            # Validation check for overlapping
            if self._overlap_check(data):
                super(Alias, self).save()
