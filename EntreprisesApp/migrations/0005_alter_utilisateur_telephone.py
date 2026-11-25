from django.db import migrations, models
import EntreprisesApp.models


class Migration(migrations.Migration):

    dependencies = [
        ('EntreprisesApp', '0004_repair_empty_user_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilisateur',
            name='telephone',
            field=models.CharField(
                blank=True,
                max_length=15,
                null=True,
                validators=[EntreprisesApp.models.telephone_validator],
            ),
        ),
    ]
