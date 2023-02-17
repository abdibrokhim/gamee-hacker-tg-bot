from django.contrib import admin

from .models import TGClient, Candy, Games, UserAdmin


class TGClientAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'username', 'referral', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tg_id', 'username',)


class CandyAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tg_id', 'quantity',)


class GamesAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'game_url', 'last_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tg_id', 'game_url', 'last_score',)


class UserAdminAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('username',)


admin.site.register(TGClient, TGClientAdmin)
admin.site.register(Candy, CandyAdmin)
admin.site.register(Games, GamesAdmin)
admin.site.register(UserAdmin, UserAdminAdmin)

