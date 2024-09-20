from django.contrib import admin

from blogs.models import *

# Register your models here.
class CategoriaAdmin(admin.ModelAdmin):
        search_fields=['nombre']
        list_display=('nombre','estado','fecha_creacion')
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Post)
