from django.db import models


class BitemporalModelBase(models.Model):

    id = models.IntegerField()
    row_id = models.AutoField(primary_key=True)

    start_date = models.DateTimeField(auto_add_now=True)
    end_date = models.DateTimeField(blank=True, null=True)

    txn_start_date = models.DateTimeField(auto_now_add=True)
    txn_end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = [
            ('id', 'start_date', 'end_date', 'txn_end_date'),
        ]
