from django.db.models import Q

from premier.models import *
from sema.models import *


def perform_premier_api_update(tasks=None):
    if not tasks:
        tasks = [
            'product_inventory',
            'product_pricing',
            'product_primary_image'
        ]

    msgs = []
    for index, task in enumerate(tasks, start=1):
        if task == 'product_inventory':
            print(f'{index}. Updating product inventory...')
            try:
                products = PremierProduct.objects.filter(
                    manufacturer__is_relevant=True
                )
                msgs += products.update_inventory_from_api()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'product_pricing':
            print(f'{index}. Updating product pricing...')
            try:
                products = PremierProduct.objects.filter(is_relevant=True)
                msgs += products.update_pricing_from_api()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'product_primary_image':
            print(f'{index}. Updating product primary image...')
            try:
                products = PremierProduct.objects.filter(
                    Q(is_relevant=True)
                    & (
                        Q(primary_image__isnull=True)
                        | Q(primary_image__exact='')
                    )
                )
                msgs += products.update_primary_image_from_media_root()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        else:
            msgs.append('Internal Error: Invalid task')

    info = [msg for msg in msgs if msg[:4] == 'Info']
    success = [msg for msg in msgs if msg[:7] == 'Success']
    error = [
        msg for msg in msgs
        if not msg[:4] == 'Info'
        and not msg[:7] == 'Success'
    ]
    return msgs, info, success, error


def retrieve_sema_api_data(models=None):
    if not models:
        models = [
            SemaBrand,
            SemaDataset,
            SemaYear,
            SemaMake,
            SemaModel,
            SemaSubmodel,
            SemaMakeYear,
            SemaBaseVehicle,
            SemaVehicle,
            SemaCategory,
            SemaProduct
        ]

    all_data = {}
    errors = []
    for index, model in enumerate(models, start=1):
        print(f'{index}. Retrieving {model._meta.verbose_name.title()}...')
        try:
            data = model.objects.get_api_data()
            all_data[model._meta.verbose_name] = data
        except Exception as err:
            errors.append(f'Internal Error: {err}')
            print('--- errored')
            continue
        print('--- complete')

    return all_data, errors


def perform_sema_api_import_and_unauthorize(models=None):
    if not models:
        models = [
            SemaBrand,
            SemaDataset,
            SemaYear,
            SemaMake,
            SemaModel,
            SemaSubmodel,
            SemaMakeYear,
            SemaBaseVehicle,
            SemaVehicle,
            SemaCategory,
            SemaProduct
        ]

    msgs = []
    for index, model in enumerate(models, start=1):
        print(f'{index}. Syncing {model._meta.verbose_name.title()}...')
        try:
            msgs += model.objects.import_and_unauthorize_from_api()
        except Exception as err:
            msgs.append(f'Internal Error: {err}')
            print('--- errored')
            continue
        print('--- complete')

    info = [msg for msg in msgs if msg[:4] == 'Info']
    success = [msg for msg in msgs if msg[:7] == 'Success']
    error = [
        msg for msg in msgs
        if not msg[:4] == 'Info'
        and not msg[:7] == 'Success'
    ]
    return msgs, info, success, error


def perform_sema_api_update(tasks=None):
    if not tasks:
        tasks = [
            'product_category',
            'product_vehicle'
        ]

    msgs = []
    for index, task in enumerate(tasks, start=1):
        if task == 'product_category':
            print(f'{index}. Updating product categories...')
            try:
                categories = SemaCategory.objects.filter(is_authorized=True)
                msgs += categories.perform_product_category_update()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'product_vehicle':
            print(f'{index}. Updating product vehicles...')
            try:
                brands = SemaBrand.objects.filter(is_authorized=True)
                msgs += brands.perform_product_vehicle_update()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        else:
            msgs.append('Internal Error: Invalid task')

    info = [msg for msg in msgs if msg[:4] == 'Info']
    success = [msg for msg in msgs if msg[:7] == 'Success']
    error = [
        msg for msg in msgs
        if not msg[:4] == 'Info'
        and not msg[:7] == 'Success'
    ]
    return msgs, info, success, error


premier_update = perform_premier_api_update
sema_data = retrieve_sema_api_data
sema_import = perform_sema_api_import_and_unauthorize
sema_update = perform_sema_api_update


# TODO
# sema classes update (when new brands)
#
# create items
# premier inventory update (if item)
# premier pricing update (if item)
# sema html update (if item)
#
# WARN:
# item missing prices
# item missing inventory
# item missing primary image
# item missing html
# item inventory in alberta updated to 0
# incomplete items
#
# INFO:
# non item premier products with inventory in Alberta
# item with new category

# ----
#   NEW ORDER OF EVENTS
#   1. media: save images (manual)
#   2. premier manufacturer: create (manual)
#   3. premier manufacturer: mark as relevant (manual)
#   4. premier manufacturer: add image (manual)
#   5. premier products: import by csv (manual)
#   6. premier products: update inventory (task)
#       -- all new
#   7. premier products: update relevancy (manual)
#       -- all new
#       -- use "may be relevant" as a guide
#   8. premier products: update pricing (task)
#       -- all new relevant
#   9. premier products: update primary image (task)
#       -- all new relevant
#   10 create new items
#   TODO new item tasks ..


#   DAILY PREMIER AUTOMATED TASKS
#   1. update product inventory if product manufacturer is relevant
#       send info log of possible new relevant/irrelevant products
#   2. update product pricing if product is relevant

#   DAILY MANUAL TASKS
#   1. update premier product relevancy from logs
#   2. update premier product pricing for new relevant
#   2. update premier product images for new relevant
#   2. create/delete main items


#   TODO item warnings
#   no premier product
#   premier product - not relevant
#   premier product.manufacturer - no image
#   premier product - no image
#   premier product - no price
#   premier product - no inventory
#   no sema product
#   sema product - not relevant
