from urllib import response
from django.db import models
from django.contrib.auth.models import User

class OperationLogs(models.Model):
   id = models.BigAutoField(primary_key=True)
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   method = models.CharField(max_length=10, db_index=True)
   status_code = models.PositiveSmallIntegerField(help_text='Response status code', db_index=True)
   operation = models.CharField(max_length=50)
   date = models.DateTimeField(auto_now_add=True)
   class Meta:
      db_table = 'operation_logs'
      verbose_name = 'Operation Log'
      verbose_name_plural = 'Operation Logs'
