from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class ArbiBot(models.Model):
    name          = models.CharField(max_length=20)
    create        = models.DateTimeField(auto_now_add=True)
    user          = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    EX_NAME = (('bn','bn'),('bb','bb'),('drb','drb'),('okx','okx'))
    exchanger     = models.CharField(max_length=10, choices=EX_NAME)
    target        = models.CharField(max_length=10)
    payment       = models.CharField(max_length=10)
    EX_TYPE = (('S','SEL'),('M','BUY'),)
    type          = models.CharField(max_length=5, choices=EX_TYPE, default='S')
    ex_min_qty    = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    ex_min_price  = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    enable        = models.BooleanField(default=False)

    class Meta:
        ordering = ['-create']
    def __str__(self):
        return f'{self.id}_{self.name}_{self.user}'

class Arbitrage(models.Model):
    name        = models.CharField(max_length=20)
    create      = models.DateTimeField(auto_now_add=True)
    user        = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    arbibot     = models.ManyToManyField(ArbiBot)
    target      = models.CharField(max_length=10)
    trade_min_qty    = models.FloatField(default=0, validators=[MinValueValidator(0)])
    trade_max_qty    = models.FloatField(default=0, validators=[MinValueValidator(0)])
    trade_min_profit = models.FloatField(default=0, validators=[MinValueValidator(0)])
    period      = models.PositiveIntegerField(default=10)
    payment     = models.IntegerField('money_alloc', default=0, validators=[MinValueValidator(0)])
    # MODE_TYPE = (('B', 'BOTH'), ('E', 'ENTRY'), ('L', 'LIQUI'))
    # mode        = models.CharField(max_length=5, choices=MODE_TYPE, default='B')
    run         = models.BooleanField(default=False)
    dryrun      = models.BooleanField(default=False)
    enable      = models.BooleanField(default=False)

    class Meta:
        ordering = ['-create']
    def __str__(self):
        return f'{self.id}_{self.name}_{self.user}'

class optionInfo(models.Model):
    create = models.DateTimeField(auto_now_add=True, null=True) # 거래일
    username = models.CharField(max_length=20, blank=True) # 사용자
    botname  = models.CharField(max_length=20, blank=True) # arbitrage 이름
    exname_s  = models.CharField('S_Ex',  max_length=20, blank=True) # 'okx'
    exname_b  = models.CharField('B_Ex',  max_length=20, blank=True) # 'byb'
    strike = models.CharField(max_length=20, blank=True)
    Option_Type = (('c', 'c'), ('p', 'p'))
    type  = models.CharField(max_length=2,  choices=Option_Type, blank=True) # c/p
    fee   = models.FloatField(default=0.0) # 수수료
    target  = models.CharField(max_length=10, blank=True) # target
    payment = models.CharField(max_length=10, blank=True) # payment
    bid_price = models.FloatField('매수가', default=0.0)
    ask_price = models.FloatField('매도가', default=0.0)
    bid_qty = models.FloatField('매수가', default=0.0)
    ask_qty = models.FloatField('매도가', default=0.0)
    margin  = models.FloatField('마진율', null=True, blank=True)
    remainDate = models.PositiveIntegerField(null=True, blank=True)
    arbi_rate_set = models.FloatField('설정마진율', null=True, blank=True)
    arbitrage_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-create']
    def __str__(self):
        return f'{self.id}_{self.exname_s}-{self.exname_b}_{self.username}'