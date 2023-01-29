from django.db import models
from django.db.models import Model


class Boutique(Model):
    url = models.URLField(verbose_name='Lien boutique', unique=True, max_length=400)
    name = models.CharField(verbose_name='Nom boutique', max_length=255)
    short_description = models.TextField(verbose_name='Description court',
                                         blank=True, null=True)
    category = models.CharField(verbose_name='Catégorie', max_length=255)
    city = models.CharField(verbose_name='Ville', max_length=150)
    picture = models.URLField(verbose_name='Logo', max_length=400,
                              blank=True, null=True)
    address = models.CharField(verbose_name='Adresse', max_length=300,
                               blank=True, null=True)
    phone = models.CharField(verbose_name='Téléphone', max_length=20,
                             blank=True, null=True)
    web_site = models.URLField(verbose_name='Site web', max_length=400,
                               blank=True, null=True)
    long_description = models.TextField(verbose_name='Description longue',
                                        blank=True, null=True)
    added_date = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = '1 - Boutique'
        verbose_name_plural = '1 - Boutiques'
        ordering = ('added_date',)


class Produit(Model):
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE,
                                 verbose_name='Boutique', related_name='boutique')
    url = models.URLField(verbose_name='Lien produit', unique=True, max_length=400)
    title = models.CharField(verbose_name='Titre produit', max_length=255)
    category = models.CharField(verbose_name='Catégorie produit', max_length=255)
    price = models.PositiveIntegerField(verbose_name='Prix produit', default=0)
    image_1 = models.URLField(verbose_name='Produit image 1', max_length=400,
                              blank=True, null=True)
    image_2 = models.URLField(verbose_name='Produit image 2', max_length=400,
                              blank=True, null=True)
    image_3 = models.URLField(verbose_name='Produit image 3', max_length=400,
                              blank=True, null=True)
    description = models.TextField(verbose_name='Description produit',
                                   blank=True, null=True)
    date_published = models.DateField(verbose_name='Date publication')

    def __str__(self):
        return '{} - {}'.format(self.boutique.id, self.title)

    class Meta:
        verbose_name = '1 - Produit'
        verbose_name_plural = '1 - Produits'
        ordering = ('date_published',)


class Particulier(Model):
    name = models.CharField(verbose_name='Nom utilisateur', max_length=255)
    phone = models.CharField(verbose_name='Téléphone', max_length=20,
                             blank=True, null=True, unique=True)
    city = models.CharField(verbose_name='Ville', max_length=150)
    added_date = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = '0 - Particulier'
        verbose_name_plural = '0 - Particuliers'
        ordering = ('added_date',)


class ParticulierProduit(Model):
    particulier = models.ForeignKey(Particulier, on_delete=models.CASCADE,
                                    verbose_name='Particulier', related_name='Particulier')
    url = models.URLField(verbose_name='Lien produit', max_length=400)
    title = models.CharField(verbose_name='Titre annonce', max_length=255)
    category = models.CharField(verbose_name='Catégorie annonce', max_length=255)
    price = models.PositiveIntegerField(verbose_name='Prix annonce', default=0)
    image_1 = models.URLField(verbose_name='Annonce image 1', max_length=400,
                              blank=True, null=True)
    image_2 = models.URLField(verbose_name='Annonce image 2', max_length=400,
                              blank=True, null=True)
    image_3 = models.URLField(verbose_name='Annonce image 3', max_length=400,
                              blank=True, null=True)
    description = models.TextField(verbose_name='Description annonce',
                                   blank=True, null=True)
    date_published = models.DateField(verbose_name='Date publication')

    def __str__(self):
        return '{} - {}'.format(self.particulier.id, self.title)

    class Meta:
        verbose_name = '0 - Annonce Particulier'
        verbose_name_plural = '0 - Annonces Particulier'
        unique_together = (('particulier', 'url'),)
        ordering = ('date_published',)
