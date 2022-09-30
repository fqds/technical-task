from django.db import models

# Бд, хранящая содержимое таблицы
class Record(models.Model):
    table_number = models.IntegerField()
    order_number = models.IntegerField()
    price = models.IntegerField()
    price_rubles = models.IntegerField()
    delivery_date = models.DateField()

    class Meta:
        ordering = ["table_number"]

# Список дат, в которые необходимо уведомить пользователя о сроке поставки
class NotificationQueue(models.Model):
    record_identifier = models.ForeignKey(Record, on_delete=models.CASCADE)
    delivery_date = models.DateField()
    is_worked_out = models.BooleanField(default=False)