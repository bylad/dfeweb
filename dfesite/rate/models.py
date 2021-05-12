from django.db import models

# Create your models here.
class Daily(models.Model):
    date = models.DateField()
    usd = models.FloatField()

    def __str__(self):
        return str(self.usd)

    class Meta:
        ordering = ['-date']

class Monthly(models.Model):
    date = models.DateField()
    oil = models.FloatField()
    usd = models.FloatField()

    def __str__(self):
        return str(self.oil)
