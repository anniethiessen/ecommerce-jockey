def initialize_sema():
    from sema.models import *
    from task.utils import *

    print_errors_only = True
    import_new_only = True
    filters = {}

    print_header("initializing sema", end_newline=True)

    # ------------------

    print_header("sema brands & datasets")

    print_subheader("importing sema brands")
    msgs = SemaBrand.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)

    print_subheader("importing sema datasets")
    msgs = SemaDataset.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)

    # ------------------

    print_header("sema years, makes, models, & submodels")

    print_subheader("importing sema years")
    msgs = SemaYear.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)

    print_subheader("importing sema makes")
    msgs = SemaMake.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)

    print_subheader('importing sema models')
    msgs = SemaModel.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)

    print_subheader('importing sema submodels')
    msgs = SemaSubmodel.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)

    # ------------------

    print_header("sema make years, base vehicles, vehicles, and engines")

    print_subheader("importing sema make years")
    msgs = SemaMakeYear.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)

    print_subheader("importing sema base vehicles")
    for make_year in SemaMakeYear.objects.all():
        make_years = SemaMakeYear.objects.filter(pk=make_year.pk)
        msgs = SemaBaseVehicle.objects.perform_import_from_api(make_years=make_years)
        print_messages(msgs, errors_only=print_errors_only)

    print_subheader("importing sema vehicles")
    for base_vehicle in SemaBaseVehicle.objects.all():
        base_vehicles = SemaBaseVehicle.objects.filter(pk=base_vehicle.pk)
        msgs = SemaVehicle.objects.perform_import_from_api(base_vehicles=base_vehicles)
        print_messages(msgs, errors_only=print_errors_only)

    print_subheader("importing sema engines")
    for vehicle in SemaVehicle.objects.all():
        filters = {
            'year': vehicle.base_vehicle.make_year.year.pk,
            'make_id': vehicle.base_vehicle.make_year.make.pk,
            'model_id': vehicle.base_vehicle.model.pk
        }
        msgs = SemaEngine.objects.perform_import_from_api(**filters)
        print_messages(msgs, errors_only=print_errors_only)

    # ------------------

    print_header("sema categories & products")

    print_subheader("importing sema categories")
    msgs = SemaCategory.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)

    print_subheader("importing sema products")
    msgs = SemaProduct.objects.perform_import_from_api(new_only=import_new_only, **filters)
    print_messages(msgs, errors_only=print_errors_only)