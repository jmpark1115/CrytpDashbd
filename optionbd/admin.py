from .models import *
from django.contrib import admin

@admin.register(ArbiBot)
class ArbiBotAdmin(admin.ModelAdmin):
    model = ArbiBot
    list_display = ('id', 'name', 'user', 'create', 'exchanger', 'target', 'payment', 'type', 'enable', )

@admin.register(Arbitrage)
class ArbitrageAdmin(admin.ModelAdmin):
    model = Arbitrage
    list_display = ('id', 'name', 'user', 'create', 'target', 'payment', 'enable')

@admin.register(optionInfo)
class TransAdmin(admin.ModelAdmin):
    model = optionInfo
    list_display = ('id', 'create', 'botname', 'exname_s', 'exname_b', 'strike', 'type',
                    'target', 'payment', 'ask_price', 'bid_price', 'ask_qty', 'bid_qty',
                    'margin', 'remainDate', 'arbitrage_id', 'username', )
    # list_filter = (('create', DateTimeRangeFilter), 'username', 'botname', 'type', )
    # search_fields = ('id', 'create', 'botname', 'mark', 'type',)

    '''
    class optionTrans(models.Model):
    create = models.DateTimeField(auto_now_add=True, null=True) # 거래일
    username = models.CharField(max_length=20, blank=True) # 사용자
    botname  = models.CharField(max_length=20, blank=True) # arbitrage 이름
    exname_s  = models.CharField('S_Ex',  max_length=20, blank=True) # 'okx'
    exname_b  = models.CharField('B_Ex',  max_length=20, blank=True) # 'byb'
    strike = models.CharField(max_lenghth=20, blank=True)
    Option_Type = (('c', 'c'), ('p', 'p'))
    type  = models.CharField(max_length=2,  choices=Option_Type, blank=True) # c/p
    fee   = models.FloatField(default=0.0) # 수수료
    target  = models.CharField(blank=True) # target
    payment = models.CharField(blank=True) # payment
    bid_price = models.FloatField('매수가', default=0.0)
    ask_price = models.FloatField('매도가', default=0.0)
    bid_qty = models.FloatField('매수가', default=0.0)
    ask_qty = models.FloatField('매도가', default=0.0)
    margin  = models.FloatField('마진율', null=True, blank=True)
    remainDate = models.PositiveIntegerField(null=True, blank=True)
    arbi_rate_set = models.FloatField('설정마진율', null=True, blank=True)
    arbitrage_id = models.IntegerField(null=True, blank=True)

    class Meta:
    '''