from django.db import models

# Create your models here.
class ArkFund(models.Model):
    ticker = models.CharField(max_length=4)
    file_url = models.URLField()

    def __str__(self):
        return f'{self.ticker}'


class ArkStock(models.Model):
    company = models.CharField(max_length=1024)
    ticker = models.CharField(blank=True, max_length=30)
    shares = models.IntegerField(blank=True, default=0)
    shares_delta = models.IntegerField(blank=True, null=True)
    shares_delta_percent = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    weight = models.DecimalField(decimal_places=2, max_digits=5)
    weight_delta = models.DecimalField(
        decimal_places=2, max_digits=5, blank=True, null=True)
    had_changes = models.BooleanField(default=False)
    fund = models.ForeignKey(
        'bot.ArkFund', related_name="stocks", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.fund.ticker} | {self.company}'