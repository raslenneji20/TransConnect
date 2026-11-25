from django.db import migrations
from django.utils import timezone


def repair_empty_user_ids(apps, schema_editor):
    Utilisateur = apps.get_model('EntreprisesApp', 'Utilisateur')
    database = schema_editor.connection.alias
    prefix = f"{timezone.now().strftime('%y')}user"
    used_ids = set(
        Utilisateur.objects.using(database)
        .filter(user_id__startswith=prefix)
        .values_list('user_id', flat=True)
    )

    related_fields = []
    for model in apps.get_models():
        for field in model._meta.local_fields:
            if (
                field.is_relation
                and field.remote_field
                and field.remote_field.model == Utilisateur
            ):
                related_fields.append((model, field))

    for user in Utilisateur.objects.using(database).filter(user_id='').iterator():
        for number in range(1, 100):
            new_user_id = f'{prefix}{number:02d}'
            if new_user_id not in used_ids:
                break
        else:
            raise RuntimeError('Limite annuelle de 99 utilisateurs atteinte.')

        old_user_id = user.user_id
        Utilisateur.objects.using(database).filter(
            user_id=old_user_id
        ).update(user_id=new_user_id)
        for model, field in related_fields:
            model._base_manager.using(database).filter(
                **{field.attname: old_user_id}
            ).update(**{field.attname: new_user_id})
        used_ids.add(new_user_id)


class Migration(migrations.Migration):

    dependencies = [
        ('EntreprisesApp', '0003_alter_entreprise_id'),
    ]

    operations = [
        migrations.RunPython(repair_empty_user_ids, migrations.RunPython.noop),
    ]
