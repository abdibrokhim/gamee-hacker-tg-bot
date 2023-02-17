from django.db import models


class TGClient(models.Model):
    tg_id = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    referral = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tg_id

    class Meta:
        verbose_name = 'TG Client'
        verbose_name_plural = 'TG Clients'


class Candy(models.Model):
    tg_id = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tg_id

    class Meta:
        verbose_name = 'Candy'
        verbose_name_plural = 'Candies'


class Games(models.Model):
    tg_id = models.CharField(max_length=255, blank=True, null=True)
    game_url = models.CharField(max_length=255, blank=True, null=True)
    last_score = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tg_id

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'


class UserAdmin(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

