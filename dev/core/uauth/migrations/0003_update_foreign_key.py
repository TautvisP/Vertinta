# dev/core/uauth/migrations/0003_update_foreign_key.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('uauth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermeta',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uauth.User'),
        ),
    ]