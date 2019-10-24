from premier.models import *
from sema.models import *


def perform_premier_api_update(tasks=None):
    if not tasks:
        tasks = [
            'product_inventory',
            'product_pricing'
        ]

    msgs = []
    for index, task in enumerate(tasks, start=1):
        if task == 'product_inventory':
            print(f'{index}. Updating product inventory...')
            try:
                products = PremierProduct.objects.all()
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
