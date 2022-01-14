from django.db import models

# Create your models here.
class MigrationHead(models.Model):
    objects = models.Manager()
    migration_title = models.CharField(max_length=256)
    href = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.migration_title

class MigrationData(models.Model):
    objects = models.Manager()
    migrationhead = models.ForeignKey(MigrationHead, related_name='migrations', on_delete=models.CASCADE)
    arrived = models.IntegerField()
    departed = models.IntegerField()
    gain = models.IntegerField()

    def __str__(self):
        return f"{str(self.arrived)}, {str(self.departed)}, {str(self.gain)}"

class ZagsHead(models.Model):
    objects = models.Manager()
    zags_title = models.CharField(max_length=256)
    href = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.zags_title

class ZagsData(models.Model):
    objects = models.Manager()
    zagshead = models.ForeignKey(ZagsHead, related_name='zags', on_delete=models.CASCADE)
    born = models.IntegerField()
    died = models.IntegerField()
    wedd = models.IntegerField()
    divorce = models.IntegerField()

    def __str__(self):
        return f"{str(self.born)}, {str(self.died)}, {str(self.wedd)}, {str(self.divorce)}"
