from django.test import TestCase
from alias.models import Alias
from django.utils import timezone
import datetime
from django.core.exceptions import ValidationError


class AliasTest(TestCase):
    moment = timezone.now()

    def test_insert(self):
        """
        Test case for inserting.
        """
        # Simple data insert
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one', start=self.moment,
                             end=self.moment + datetime.timedelta(hours=5))

        # Alias start at the same moment as existing one ends
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                             start=self.moment + datetime.timedelta(hours=5),
                             end=self.moment + datetime.timedelta(hours=6))

        # Alias ends at the same moment as existing one starts
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                             start=self.moment - datetime.timedelta(hours=5),
                             end=self.moment)

        # Infinite alias
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                             start=self.moment + datetime.timedelta(hours=7),
                             end=None)

        # We are to get 4 aliases
        result = len(Alias.objects.all())
        self.assertEqual(4, result)

    def test_overlapping_in_finite(self):
        """
        Test case for overlapping of finite aliases:
         Finite aliases
            1. Identical alias
            2. New alias ends at the moment of an existing one (starts before), ValidationError is expected.
            3. New alias starts at the moment of an existing one (ends after), ValidationError is expected.
            4. New alias starts before an existing one and ends after, ValidationError is expected.

         Finite and infinite aliases
            5. New infinite-alias starts before an existing one, ValidationError is expected.
        """

        mistakes = 0

        # Filling in database
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one', start=self.moment,
                             end=self.moment + datetime.timedelta(hours=5))

        # Overlapping check 1
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-one', start=self.moment,
                                 end=self.moment + datetime.timedelta(hours=5))
        except ValidationError:
            mistakes += 1

        # Overlapping check 2
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                                 start=self.moment - datetime.timedelta(hours=2),
                                 end=self.moment + datetime.timedelta(hours=3))
        except ValidationError:
            mistakes += 1

        # Overlapping check 3
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                                 start=self.moment + datetime.timedelta(hours=1),
                                 end=self.moment + datetime.timedelta(hours=10))
        except ValidationError:
            mistakes += 1

        # Overlapping check 4
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                                 start=self.moment - datetime.timedelta(hours=1),
                                 end=self.moment + datetime.timedelta(hours=10))
        except ValidationError:
            mistakes += 1

        # Overlapping check 5
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                                 start=self.moment - datetime.timedelta(hours=1),
                                 end=None)
        except ValidationError:
            mistakes += 1

        # 5 mistakes are expected
        self.assertEqual(5, mistakes)

    def test_overlapping_infinite(self):
        """
        Test case for overlapping of finite and infinite aliases:
            1. New infinite alias starts before start of an existing one, ValidationError is expected.
            1. New infinite alias starts after start of an existing one, ValidationError is expected.
        """

        mistakes = 0

        # Filling in database with infinite alias
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one', start=self.moment,
                             end=None)

        # Overlapping check 1
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                                 start=self.moment - datetime.timedelta(hours=1),
                                 end=None)
        except ValidationError:
            mistakes += 1

        # Overlapping check 2
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                                 start=self.moment + datetime.timedelta(hours=1),
                                 end=None)
        except ValidationError:
            mistakes += 1

        self.assertEqual(2, mistakes)

    def test_uniqueness_check(self):
        """
        Test case for incorrect input avoiding.
            1. Aliases with same alias value must refer to the same target, ValidationError is expected.
            2. Alias can not end before start, ValidationError is expected.
        """

        mistakes = 0

        # Filling in database.
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one', start=self.moment,
                             end=self.moment + datetime.timedelta(hours=5))

        # 1
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-two', start=self.moment,
                                 end=self.moment + datetime.timedelta(hours=5))
        except ValidationError:
            mistakes += 1

        # 2
        try:
            Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                                 start=self.moment - datetime.timedelta(hours=3),
                                 end=self.moment - datetime.timedelta(hours=5))
        except ValidationError:
            mistakes += 1

        self.assertEqual(2, mistakes)

    def test_get_aliases(self):
        """Test case for get_aliases method"""
        # Filling in database.
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one', start=self.moment,
                             end=self.moment + datetime.timedelta(hours=5))

        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                             start=self.moment - datetime.timedelta(hours=3),
                             end=self.moment)

        # 1 alias is expected
        result = Alias.get_aliases(target='test-alias-target-one', from_=self.moment,
                                   to=self.moment + datetime.timedelta(days=2))
        self.assertEqual(1, len(result))

        # 1 aliases is expected, because we return set()
        result = Alias.get_aliases(target='test-alias-target-one',
                                   from_=self.moment - datetime.timedelta(hours=1),
                                   to=self.moment + datetime.timedelta(days=2))
        self.assertEqual(1, len(result))

        # No aliases in that time range
        result = Alias.get_aliases(target='test-alias-target-one', from_=self.moment + datetime.timedelta(days=1),
                                   to=self.moment + datetime.timedelta(days=2))
        self.assertEqual(0, len(result))

        # Creating an alias with new alias value
        Alias.objects.create(alias='test-alias-two', target='test-alias-target-one',
                             start=self.moment - datetime.timedelta(hours=3),
                             end=self.moment)
        # 2 aliases are expected, because we return set()
        result = Alias.get_aliases(target='test-alias-target-one',
                                   from_=self.moment - datetime.timedelta(hours=1),
                                   to=self.moment + datetime.timedelta(days=2))
        self.assertEqual(2, len(result))

        # Create an infinite alias
        Alias.objects.create(alias='test-alias-three', target='test-alias-target-two',
                             start=self.moment,
                             end=None)

        # 1 aliases is expected
        result = Alias.get_aliases(target='test-alias-target-two',
                                   from_=self.moment + datetime.timedelta(days=1),
                                   to=self.moment + datetime.timedelta(days=2))
        self.assertEqual(1, len(result))

    def test_alias_replace(self):
        """Test case for alias_replace method"""
        mistakes = 0
        # Filling in database.
        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one', start=self.moment,
                             end=self.moment + datetime.timedelta(hours=5))

        Alias.objects.create(alias='test-alias-one', target='test-alias-target-one',
                             start=self.moment - datetime.timedelta(hours=3),
                             end=self.moment)
        try:
            Alias.alias_replace(existing_alias='test-alias-one', replace_at=self.moment + datetime.timedelta(hours=2),
                                new_alias_value='test-alias-one')
        except ValidationError:
            mistakes += 1
        self.assertEqual(1, mistakes)

        # end value for new alias will be set as None
        Alias.alias_replace(existing_alias='test-alias-one', replace_at=self.moment + datetime.timedelta(hours=2),
                            new_alias_value='test-alias-two')

        # 1 alias is expected
        result = Alias.get_aliases(target='test-alias-target-one', from_=self.moment + datetime.timedelta(days=2),
                                   to=self.moment + datetime.timedelta(days=3))
        self.assertEqual(1, len(result))
