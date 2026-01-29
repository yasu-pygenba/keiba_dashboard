from django.db import models

class Summary(models.Model):
    axis_col = models.CharField(max_length=10) #印
    bet_type = models.CharField(max_length=20) #券種

    total_bet_yen = models.IntegerField()
    total_return_yen = models.IntegerField()
    n_bets = models.IntegerField()
    n_hits = models.IntegerField()

    hit_rate = models.FloatField()
    roi = models.FloatField()

    kaisai_date = models.CharField(max_length=8, db_index=True) #yyyymmdd

    created_at = models.DateTimeField(auto_now_add=True)

    def profit_yen(self) -> int:
        return self.total_return_yen - self.total_bet_yen
    
    def __str__(self):
        return f'{self.kaisai_date} {self.axis_col} {self.bet_type}'
    
class PerRace(models.Model):
    # race_id = 202601240601　なら先頭8桁が開催日
    race_id = models.CharField(max_length=20, db_index=True)
    kaisai_date = models.CharField(max_length=8, db_index=True)

    venue = models.CharField(max_length=10, db_index=True) # 開催=競馬場
    distance = models.IntegerField(null=True, blank=True) # 距離
    surface = models.CharField(max_length=5, blank=True, default='') # コース
    weather = models.CharField(max_length=10, blank=True, default='') # 天候
    baba = models.CharField(max_length=10, blank=True, default='') # 馬場

    axis_col = models.CharField(max_length=10, db_index=True) # 予想者名：印/印2/印3
    axis_mark = models.CharField(max_length=10, blank=True, default='') # ◎など
    bet_type = models.CharField(max_length=20, db_index=True)

    total_bet_yen = models.IntegerField()
    total_return_yen = models.FloatField() # pklに小数の値あり
    n_bets = models.IntegerField()
    n_hits = models.IntegerField()

    hit_rate = models.FloatField()
    roi = models.FloatField() # pkl列名はROI=回収率

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['kaisai_date', 'venue']),
            models.Index(fields=['kaisai_date', 'venue', 'axis_col']),
            models.Index(fields=['kaisai_date', 'venue', 'bet_type']),
        ]

    def profit_yen(self) -> float:
        return float(self.total_return_yen) - float(self.total_bet_yen)
    
    def __str__(self):
        return f'{self.race_id} {self.venue} {self.axis_col} {self.bet_type}'