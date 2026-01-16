from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"  # Frecuencia con la que cambian las páginas
    priority = 0.5  # Prioridad para los motores de búsqueda

    def items(self):
        # Lista de nombres de vistas que quieres incluir en el sitemap
        return ['index', 'nosotros', 'contacto', 'pqrs', 'servicios','blog']

    def location(self, item):
        # Utiliza el nombre de la vista para generar la URL
        return reverse(item)
