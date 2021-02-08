# # from django.core import serializers
# from django.contrib.sessions import serializers
# from rest_framework import serializers
# from .models import Alias
# from rest_framework.serializers import ValidationError
#
#
# class AliasSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Alias
#         fields = ['id', 'alias', 'target', 'start', 'end']
#
#     def _overlap_check(self, data):
#         """Function that checks new alias initialization for overlapping with existing one
#         >> a = Alias.objects.create(alias='useful-object', target='some-target-one',\
#             start = moment + timedelta(hours=80), end = moment + timedelta(hours=90))
#         >> a.save()
#         django.core.exceptions.ValidationError: ['Aliases can not overlap!']"""
#         for item in data:
#             if self.pk != item.pk:      # Replacing values, current alias will be compared with itself - avoid that
#                 # For two finite gaps
#                 if all((item.end, self.end)):
#                     # Starting point inside of existing gap
#                     if item.start <= self.start <= item.end:
#                         raise ValidationError('Aliases can not overlap!')
#                     # Ending point inside of existing gap
#                     elif item.start < self.end < item.end:
#                         raise ValidationError('Aliases can not overlap!')
#                     # New gap covers existing one
#                     elif (self.start < item.start) and (self.end > item.end):
#                         raise ValidationError('Aliases can not overlap!')
#
#                 # For infinite and finite gaps
#                 elif self.end or item.end:
#                     # Creating of finite gap
#                     if self.end:
#                         if not (self.end <= item.start):
#                             raise ValidationError('Aliases can not overlap!')
#                     # Creating of infinite gap
#                     else:
#                         if not (self.start >= item.end):
#                             raise ValidationError('Aliases can not overlap!')
#
#                 # Two infinite gaps
#                 else:
#                     raise ValidationError('Aliases can not overlap!')
#
#         return True
#
#     def _alias_uniqueness_check(self, data):
#         """Checks for uniqueness of alias target. Aliases with same alias value can not
#         refer to different targets"""
#         for item in data:
#             if self.target != item.target:
#                 raise ValidationError(f'Aliases with same alias value must refer to the same target! '
#                                       f'Alias "{item.alias}" already refers to "{item.target}" target.')
#         return True
#
#     def validate(self, attrs):
#         data = Alias.objects.filter(alias=self.alias)
