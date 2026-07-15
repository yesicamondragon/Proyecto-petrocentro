import io

import openpyxl
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import InventoryCategory, InventoryItem, Ubicacion


class BaseInventoryCrudTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='adminbases',
            email='adminbases@example.com',
            password='secret123',
        )
        self.client.force_login(self.user)

    def test_crear_editar_y_eliminar_base(self):
        response = self.client.post(reverse('crear_base'), {'nombre': 'Base Test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Ubicacion.objects.filter(nombre='Base Test').exists())

        base = Ubicacion.objects.get(nombre='Base Test')
        response = self.client.post(
            reverse('editar_base', args=[base.idUbicacion]),
            {'nombre': 'Base Actualizada'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        base.refresh_from_db()
        self.assertEqual(base.nombre, 'Base Actualizada')

        response = self.client.get(reverse('eliminar_base', args=[base.idUbicacion]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Ubicacion.objects.filter(pk=base.idUbicacion).exists())

    def test_exportar_inventario_excel_con_columnas_de_tabla(self):
        category = InventoryCategory.objects.create(name='Categoria Prueba')
        base = Ubicacion.objects.create(nombre='Base Export')
        InventoryItem.objects.create(
            sku='SKU-001',
            name='Equipo Export',
            category=category,
            base=base,
            current_stock=5,
            unit_of_measure='UNIDAD',
            equipment_type='ACTIVO',
            owner='Proveedor Test',
            status='OPERATIVO',
            description='Observación export',
            technical_spec='Especificación',
            brand='Marca A',
            serial='SER-001',
            tag='TAG-001',
            length=2.5,
            width=1.5,
            height=1.0,
            weight=10.0,
            created_at='2026-01-01T10:00:00Z',
        )

        response = self.client.get(reverse('exportar_inventario_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])

        workbook = openpyxl.load_workbook(filename=io.BytesIO(response.content))
        sheet = workbook.active
        headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
        self.assertEqual(headers[0], 'Tipo de equipo')
        self.assertEqual(headers[1], 'Fecha de creación')
        self.assertEqual(headers[2], 'Categoría')
        self.assertEqual(headers[-1], 'Acciones')
