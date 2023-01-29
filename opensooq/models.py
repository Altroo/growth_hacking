from django.db import models
from django.db.models import Model


class OpenSooqBoutique(Model):
    country = models.CharField(verbose_name='Pays boutique', max_length=255)
    url = models.URLField(verbose_name='Lien boutique', unique=True, max_length=2000)
    name = models.CharField(verbose_name='Nom boutique', max_length=255)
    category = models.CharField(verbose_name='Catégorie', max_length=255)
    city = models.CharField(verbose_name='Ville', max_length=150)
    picture = models.URLField(verbose_name='Logo', max_length=2000,
                              blank=True, null=True)
    address = models.CharField(verbose_name='Adresse', max_length=300,
                               blank=True, null=True)
    phone = models.CharField(verbose_name='Téléphone', max_length=20,
                             blank=True, null=True)
    description = models.TextField(verbose_name='Description',
                                   blank=True, null=True)
    added_date = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = '0 - OpenSooq Boutique'
        verbose_name_plural = '0 - OpenSooq Boutiques'
        ordering = ('added_date',)


class OpenSooqBoutiqueProduit(Model):
    boutique = models.ForeignKey(OpenSooqBoutique, on_delete=models.CASCADE,
                                 verbose_name='Boutique', related_name='open_sooq_boutique')
    url = models.URLField(verbose_name='Lien produit', max_length=2000)
    title = models.CharField(verbose_name='Titre produit', max_length=255)
    category = models.CharField(verbose_name='Catégorie produit', max_length=255)
    price = models.FloatField(verbose_name='Prix produit', default=0.0)
    image_1 = models.URLField(verbose_name='Produit image 1', max_length=2000,
                              blank=True, null=True)
    image_2 = models.URLField(verbose_name='Produit image 2', max_length=2000,
                              blank=True, null=True)
    image_3 = models.URLField(verbose_name='Produit image 3', max_length=2000,
                              blank=True, null=True)
    description = models.TextField(verbose_name='Description produit',
                                   blank=True, null=True)
    date_published = models.DateField(verbose_name='Date publication')

    def __str__(self):
        return '{} - {}'.format(self.boutique.id, self.title)

    class Meta:
        verbose_name = '0 - OpenSooq Produit'
        verbose_name_plural = '0 - OpenSooq Produits'
        ordering = ('date_published',)
        unique_together = (('boutique', 'url'), )


class OpenSooqParticulier(Model):
    country = models.CharField(verbose_name='Pays particulier', max_length=255)
    name = models.CharField(verbose_name='Nom utilisateur', max_length=255)
    phone = models.CharField(verbose_name='Téléphone', max_length=20,
                             blank=True, null=True, unique=True)
    city = models.CharField(verbose_name='Ville', max_length=150)
    added_date = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = '1 - OpenSooq Particulier'
        verbose_name_plural = '1 - OpenSooq Particuliers'
        ordering = ('added_date',)


class OpenSooqParticulierProduit(Model):
    particulier = models.ForeignKey(OpenSooqParticulier, on_delete=models.CASCADE,
                                    verbose_name='Particulier', related_name='open_sooq_particulier')
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
        verbose_name = '1 - OpenSooq Particulier ads'
        verbose_name_plural = '1 - OpenSooq Particulier ads'
        unique_together = (('particulier', 'url'),)
        ordering = ('date_published',)
