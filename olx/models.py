from django.db import models
from django.db.models import Model


class Olx(Model):
    name = models.CharField(verbose_name='Nom utilisateur', max_length=255)
    city = models.CharField(verbose_name='Ville', max_length=150)
    phone = models.CharField(verbose_name='Téléphone', max_length=20,
                             blank=True, null=True, unique=True)
    added_date = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = '0 - Olx Particulier'
        verbose_name_plural = '0 - Olx Particuliers'
        ordering = ('added_date',)


class OlxProduit(Model):
    particulier = models.ForeignKey(Olx, on_delete=models.CASCADE,
                                    verbose_name='Particulier', related_name='olx')
    url = models.URLField(verbose_name='Lien produit', max_length=2000)
    title = models.CharField(verbose_name='Titre annonce', max_length=255)
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
    date_published = models.DateField(verbose_name='Date publication')

    def __str__(self):
        return '{} - {}'.format(self.particulier.id, self.title)

    class Meta:
        verbose_name = '0 - Olx produit'
        verbose_name_plural = '0 - Olx produits'
        unique_together = (('particulier', 'url'),)
        ordering = ('date_published',)
