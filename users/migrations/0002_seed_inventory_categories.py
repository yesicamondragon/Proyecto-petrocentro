from django.db import migrations

def create_technical_categories(apps, schema_editor):
    InventoryCategory = apps.get_model('users', 'InventoryCategory')
    categories = [
        "Proceso Presurizado",
        "Proceso atmosférico",
        "Inyección Bombeo y Compresión",
        "Control presión en Superficie",
        "Quemadores Gas",
        "Tubería y Accesorios",
        "Cargaderos",
        "Tableros de control y Distribución",
        "Generación e Iluminación",
        "Laboratorio y Metrología",
        "Medición Proceso",
        "HSE",
        "Campamento",
        "Tecnología",
        "Materiales de Instrumentación",
        "Herramienta",
        "Ferreteria",
    ]
    for cat_name in categories:
        InventoryCategory.objects.get_or_create(
            name=cat_name,
            defaults={'description': f'Categoría técnica para {cat_name}'}
        )
def remove_categories(apps, schema_editor):
    InventoryCategory = apps.get_model('users', 'InventoryCategory')
    categories = [
        "Proceso Presurizado", "Proceso atmosférico", "Inyección Bombeo y Compresión",
        "Control presión en Superficie", "Quemadores Gas", "Tubería y Accesorios",
        "Cargaderos", "Tableros de control y Distribución", "Generación e Iluminación",
        "Laboratorio y Metrología", "Medición Proceso", "HSE", "Campamento",
        "Tecnología", "Materiales de Instrumentación", "Herramienta", "Ferreteria",
    ]
    InventoryCategory.objects.filter(name__in=categories).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_technical_categories, remove_categories),
    ]