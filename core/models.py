from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    office = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    start_date = models.DateField()
    salary = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class ImpactActions(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    campaign_name = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
    payout = models.DecimalField(max_digits=6, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    event_date = models.DateField()


class SovrnTransactions(models.Model):
    commission_id = models.CharField(max_length=100, primary_key=True)
    campaign_name = models.CharField(max_length=100)
    click_date = models.DateField()
    commission_date = models.DateField()
    device_type = models.CharField(max_length=50)
    merchant_name = models.CharField(max_length=100)
    order_value = models.DecimalField(max_digits=10, decimal_places=2)
    publisher_revenue = models.DecimalField(max_digits=6, decimal_places=2)


class CJTransactions(models.Model):
    commission_id = models.CharField(max_length=100, primary_key=True)
    action_tracker_name = models.CharField(max_length=100)
    advertiser_name = models.CharField(max_length=100)
    website_name = models.CharField(max_length=50)
    posting_date = models.DateField()
    publisher_commission_amount = models.DecimalField(max_digits=6,decimal_places=2)
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
