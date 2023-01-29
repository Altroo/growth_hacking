from django.db import models
from django.db.models import Model


class Mubawab(Model):
    name = models.CharField(verbose_name='Nom utilisateur', max_length=255, blank=True, null=True)
    country = models.CharField(verbose_name='Country', max_length=150,
                               blank=True, null=True, default='Morocco')
    city = models.CharField(verbose_name='Ville', max_length=150)
    phone = models.CharField(verbose_name='Téléphone', max_length=20,
                               blank=True, null=True, unique=True)
    added_date = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return '{}'.format(self.phone)

    class Meta:
        verbose_name = '0 - Mubawab Particulier'
        verbose_name_plural = '0 - Mubawab Particuliers'
        ordering = ('added_date',)


class MubawabProduit(Model):
    particulier = models.ForeignKey(Mubawab, on_delete=models.CASCADE,
                                    verbose_name='Particulier', related_name='mubawab')
    url = models.URLField(verbose_name='Lien produit', max_length=2000)
    title = models.CharField(verbose_name='Titre annonce', max_length=255)
    type_annonce = models.CharField(verbose_name='Type d\'annonce', max_length=255, default=None)
    category = models.CharField(verbose_name='Catégorie annonce', max_length=255)
    price = models.FloatField(verbose_name='Prix annonce', default=0.0)
    image_1 = models.URLField(verbose_name='Annonce image 1', max_length=2000,
                              blank=True, null=True)
    image_2 = models.URLField(verbose_name='Annonce image 2', max_length=2000,
                              blank=True, null=True)
    image_3 = models.URLField(verbose_name='Annonce image 3', max_length=2000,
                              blank=True, null=True)
    description = models.TextField(verbose_name='Description annonce',
                                   blank=True, null=True)
    date_published = models.DateField(verbose_name='Date publication', auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.particulier.id, self.title)

    class Meta:
        verbose_name = '0 - Mubawab produit'
        verbose_name_plural = '0 - Mubawab produits'
        unique_together = (('particulier', 'url'),)
        ordering = ('date_published',)
