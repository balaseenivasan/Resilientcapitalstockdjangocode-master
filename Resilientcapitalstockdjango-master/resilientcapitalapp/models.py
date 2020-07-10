from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    portfolio_site = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)
    def __str__(self):
        return self.user.username

class SpNasdaqDmaData(models.Model):
    date = models.DateField('Date')
    sp500 = models.FloatField()
    dma50 = models.FloatField()

class SpNasdaq200DmaData(models.Model):
    date = models.DateField('Date')
    sp500 = models.FloatField()
    dma200 = models.FloatField()


class SpIssuesData(models.Model):
    date = models.DateField('Date')
    sp500 = models.FloatField()
    SPUpIssuesRadio = models.FloatField()

class SpRsi(models.Model):
    date = models.DateField('Date')
    sp500 = models.FloatField()
    SPRsi70 = models.FloatField()
    SPRsi30 = models.FloatField()

class SpBollingerbands(models.Model):
    date = models.DateField('Date')
    sp500 = models.FloatField()
    SPupperBollingerBand = models.FloatField()
    SPlowerBollingerBand = models.FloatField()

class Spnewhighlow(models.Model):
    date = models.DateField('Date')
    sp500 = models.FloatField()
    SP52weekhigh = models.FloatField()
    SP52weeklow = models.FloatField()
    SPSPhighlow = models.FloatField()
    SP24weekhigh = models.FloatField()
    SP24weeklow = models.FloatField()

class SPcorrection(models.Model):
    date = models.DateField('Date')
    sp500 = models.FloatField()
    Spcorrection = models.FloatField()

class SPbearmarket(models.Model):
    date = models.DateField('Date')
    sp500 = models.FloatField()
    Spbearmarket = models.FloatField()

class NasdaqDmaData(models.Model):
    date = models.DateField('Date')
    nasdaq100 = models.FloatField()
    dma50 = models.FloatField()

class Nasdaq200DmaData(models.Model):
    date = models.DateField('Date')
    nasdaq100 = models.FloatField()
    dma200 = models.FloatField()

class NasdaqIssuesData(models.Model):
    date = models.DateField('Date')
    nasdaq100 = models.FloatField()
    nasdaqUpIssuesRadio = models.FloatField()

class NasdaqRsi(models.Model):
    date = models.DateField('Date')
    nasdaq100 = models.FloatField()
    NasdaqRsi70 = models.FloatField()
    NasdaqRsi30 = models.FloatField()

class NasdaqBollingerbands(models.Model):
    date = models.DateField('Date')
    nasdaq100 = models.FloatField()
    NasdaqupperBollingerBand = models.FloatField()
    NasdaqlowerBollingerBand = models.FloatField()

class Nasdaqnewhighlow(models.Model):
    date = models.DateField('Date')
    nasdaq100 = models.FloatField()
    Nasdaq52weekhigh = models.FloatField()
    Nasdaq52weeklow = models.FloatField()
    Nasdaqhighlow = models.FloatField()
    Nasdaq24weekhigh = models.FloatField()
    Nasdaq24weeklow = models.FloatField()