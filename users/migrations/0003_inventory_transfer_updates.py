from django.db import migrations, models
import django.db.models.deletion

# This migration was causing issues due to conflicting dependencies and field removals.
# It's being modified to only add the necessary fields to StockTransaction
# and ensure it depends on the correct state of InventoryItem.
class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_seed_inventory_categories'),
        ('users', '0017_remove_inventoryitem_location_inventoryitem_base_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktransaction',
            name='destination_base',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers_in', to='users.ubicacion', verbose_name='Base Destino'),
        ),
        migrations.AddField(
            model_name='stocktransaction',
            name='origin_base',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers_out', to='users.ubicacion', verbose_name='Base Origen'),
        ),
    ]