from django.db import models

# Create your models here.
class PriceNews(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=256)
    href = models.CharField(max_length=256)
    # href_main = models.CharField(max_length=256)
    # href_petrol = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.title

    # class Meta:
    #     ordering = ['-pub_date']


class PriceData(models.Model):
    objects = models.Manager()
    pricenews = models.ForeignKey(PriceNews, related_name='products', on_delete=models.CASCADE)
    product = models.CharField(max_length=256)
    price = models.FloatField()

    def __str__(self):
        return self.product

class PricePetrolHead(models.Model):
    objects = models.Manager()
    # pricenews = models.ForeignKey(PriceNews, related_name='pethead', on_delete=models.CASCADE)
    petrol_title = models.CharField(max_length=256)
    href = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.petrol_title

class PricePetrolData(models.Model):
    objects = models.Manager()
    # pricenews = models.ForeignKey(PriceNews, related_name='petrols', on_delete=models.CASCADE)
    pricepetrolhead = models.ForeignKey(PricePetrolHead, related_name='petrols', on_delete=models.CASCADE)
    petrol = models.CharField(max_length=256)
    price = models.FloatField()

    def __str__(self):
        return self.petrol
