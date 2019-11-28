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
                msgs += products.perform_inventory_update_from_api()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'product_pricing':
            print(f'{index}. Updating product pricing...')
            try:
                products = PremierProduct.objects.filter(is_relevant=True)
                msgs += products.perform_pricing_update_from_api()
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
                msgs += products.perform_primary_image_update_from_media_root()
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
            SemaEngine,
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
            SemaEngine,
            SemaCategory,
            SemaProduct
        ]

    msgs = []
    for index, model in enumerate(models, start=1):
        print(f'{index}. Syncing {model._meta.verbose_name.title()}...')
        try:
            msgs += model.objects.perform_import_from_api()
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
            'dataset_categories',
            'dataset_vehicles',
            'category_products',
            'product_vehicles',
            'product_descriptions',
            'product_digital_assets',
            'product_html',
        ]

    msgs = []
    for index, task in enumerate(tasks, start=1):
        if task == 'dataset_categories':
            print(f'{index}. Updating dataset categories...')
            try:
                qs = SemaDataset.objects.filter(is_authorized=True)
                msgs += qs.perform_dataset_categories_update_from_api()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'dataset_vehicles':
            print(f'{index}. Updating dataset vehicles...')
            try:
                qs = SemaDataset.objects.filter(is_authorized=True)
                msgs += qs.perform_dataset_vehicles_update_from_api()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'category_products':
            print(f'{index}. Updating category products...')
            try:
                qs = SemaCategory.objects.filter(is_authorized=True)
                msgs += qs.perform_category_products_update_from_api()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'product_vehicles':
            print(f'{index}. Updating product vehicles...')
            try:
                qs = SemaProduct.objects.filter(is_authorized=True)
                msgs += qs.perform_product_vehicles_update_from_api()
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'product_descriptions':
            print(f'{index}. Updating product descriptions...')
            try:
                from sema.models import SemaDescriptionPiesAttribute
                qs = SemaProduct.objects.filter(is_relevant=True)
                msgs += qs.perform_pies_attribute_update_from_api(
                    pies_attr_model=SemaDescriptionPiesAttribute
                )
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'product_digital_assets':
            print(f'{index}. Updating product assets...')
            try:
                from sema.models import SemaDigitalAssetsPiesAttribute
                qs = SemaProduct.objects.filter(is_relevant=True)
                msgs += qs.perform_pies_attribute_update_from_api(
                    pies_attr_model=SemaDigitalAssetsPiesAttribute
                )
                print('--- complete')
            except Exception as err:
                msgs.append(f'Internal Error: {err}')
                print('--- errored')
        elif task == 'product_html':
            print(f'{index}. Updating product HTML...')
            try:
                qs = SemaProduct.objects.filter(is_relevant=True)
                msgs += qs.perform_product_html_update_from_api()
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
# PERIODICALLY & (WHEN NEW BRANDS)
# sema brand import
# sema dataset import
# sema year import
# sema make import
# sema model import
# sema submodel import
# sema make year import
# sema base vehicle import
# sema vehicle import
# sema category import
# sema product import

# sema dataset update categories
# sema dataset update vehicles
# sema category update products
# sema products update vehicles
#
# sema mark relevant/create item
# sema brand image
# sema product html update
# sema product pies update

# premier import manufacturer csv
# premier inventory update

# premier mark relevant/create item
# premier link images
# premier pricing update
#
#
# INFO/WARNINGS:
# may be relevant
# shopify changes

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
