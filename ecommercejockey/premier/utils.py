import os


def premier_product_image_path(instance, filename):
    return os.path.join(
        'premier',
        instance.manufacturer.slug,
        'product',
        'images',
        filename
    )


def premier_manufacturer_image_path(instance, filename):
    return os.path.join(
        'premier',
        instance.slug,
        'manufacturer',
        'images',
        filename
    )
