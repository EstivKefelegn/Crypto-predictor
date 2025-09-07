from django.db import models

class CoinHistory(models.Model):
    coin_symbol = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    high_price = models.DecimalField(max_digits=20, decimal_places=8)
    low_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=20, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['coin_symbol', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.coin_symbol} - {self.timestamp}"