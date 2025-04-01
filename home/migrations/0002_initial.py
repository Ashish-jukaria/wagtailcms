# Generated by Django 5.1.6 on 2025-03-31 10:47

import django.db.models.deletion
import modelcluster.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='customimage',
            name='uploaded_by_user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='uploaded by user'),
        ),
        migrations.AddField(
            model_name='committeememeber',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='committee_member_image', to='home.customimage'),
        ),
        migrations.AddField(
            model_name='carouselitem',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='home.customimage'),
        ),
        migrations.AddField(
            model_name='customrendition',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='renditions', to='home.customimage'),
        ),
        migrations.AddField(
            model_name='designation',
            name='member',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='designations', to='home.committeememeber'),
        ),
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_image', to='home.customimage'),
        ),
        migrations.AddField(
            model_name='event',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='home.eventspage'),
        ),
        migrations.AddField(
            model_name='awards_presentation',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='events_awards', to='home.eventspage'),
        ),
        migrations.AddField(
            model_name='faqitem',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='faq_items', to='home.aboutpage'),
        ),
        migrations.AddField(
            model_name='carouselitem',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='carousel_items', to='home.homepage'),
        ),
        migrations.AddField(
            model_name='iess',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='iess_events', to='home.eventspage'),
        ),
        migrations.AddField(
            model_name='imagegalleryitem',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='home.customimage'),
        ),
        migrations.AddField(
            model_name='imagegalleryitem',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='home.imagegallerypage'),
        ),
        migrations.AddField(
            model_name='inee',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='inee_events', to='home.eventspage'),
        ),
        migrations.AddField(
            model_name='otherevents',
            name='flag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flag_image', to='home.customimage'),
        ),
        migrations.AddField(
            model_name='otherevents',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='other_events', to='home.eventspage'),
        ),
        migrations.AddField(
            model_name='productpanelitem',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_panel_items', to='home.aboutpage'),
        ),
        migrations.AddField(
            model_name='webinar_seminar',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='events_webinar', to='home.eventspage'),
        ),
        migrations.AlterUniqueTogether(
            name='customrendition',
            unique_together={('image', 'filter_spec', 'focal_point_key')},
        ),
    ]
