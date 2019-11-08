from rest_framework.serializers import Serializer


class ProductOrderCreateSerializer(Serializer):
    def update(self, instance, validated_data):
        print(validated_data)
        x = {
            'id': 820982911946154508,
            'email': 'jon@doe.ca',
            'closed_at': None,
            'created_at': '2019-11-07T13:19:14-07:00',
            'updated_at': '2019-11-07T13:19:14-07:00',
            'number': 234,
            'note': None,
            'token': '123456abcd',
            'gateway': None,
            'test': True,
            'total_price': '493.18',
            'subtotal_price': '483.18',
            'total_weight': 0,
            'total_tax': '0.00',
            'taxes_included': False,
            'currency': 'CAD',
            'financial_status': 'voided',
            'confirmed': False,
            'total_discounts': '5.00',
            'total_line_items_price': '488.18',
            'cart_token': None,
            'buyer_accepts_marketing': True,
            'name': '#9999',
            'referring_site': None,
            'landing_site': None,
            'cancelled_at': '2019-11-07T13:19:14-07:00',
            'cancel_reason': 'customer',
            'total_price_usd': None,
            'checkout_token': None,
            'reference': None,
            'user_id': None,
            'location_id': None,
            'source_identifier': None,
            'source_url': None,
            'processed_at': None,
            'device_id': None,
            'phone': None,
            'customer_locale': 'en',
            'app_id': None,
            'browser_ip': None,
            'landing_site_ref': None,
            'order_number': 1234,
            'discount_applications': [
                {
                    'type': 'manual',
                    'value': '5.0',
                    'value_type': 'fixed_amount',
                    'allocation_method': 'one',
                    'target_selection': 'explicit',
                    'target_type': 'line_item',
                    'description': 'Discount',
                    'title': 'Discount'
                }
            ],
            'discount_codes': [],
            'note_attributes': [],
            'payment_gateway_names': [
                'visa',
                'bogus'
            ],
            'processing_method': '',
            'checkout_id': None,
            'source_name': 'web',
            'fulfillment_status': 'pending',
            'tax_lines': [],
            'tags': '',
            'contact_email': 'jon@doe.ca',
            'order_status_url': 'https://diesler-corp.myshopify.com/8018133082/orders/123456abcd/authenticate?key=abcdefg',
            'presentment_currency': 'CAD',
            'total_line_items_price_set': {
                'shop_money': {
                    'amount': '488.18',
                    'currency_code': 'CAD'
                },
                'presentment_money': {
                    'amount': '488.18',
                    'currency_code': 'CAD'
                }
            },
            'total_discounts_set': {
                'shop_money': {
                    'amount': '5.00',
                    'currency_code': 'CAD'
                },
                'presentment_money': {
                    'amount': '5.00',
                    'currency_code': 'CAD'
                }
            },
            'total_shipping_price_set': {
                'shop_money': {
                    'amount': '10.00',
                    'currency_code': 'CAD'
                },
                'presentment_money': {
                    'amount': '10.00',
                    'currency_code': 'CAD'
                }
            },
            'subtotal_price_set': {
                'shop_money': {
                    'amount': '483.18',
                    'currency_code': 'CAD'
                },
                'presentment_money': {
                    'amount': '483.18',
                    'currency_code': 'CAD'
                }
            },
            'total_price_set': {
                'shop_money': {
                    'amount': '493.18',
                    'currency_code': 'CAD'
                },
                'presentment_money': {
                    'amount': '493.18',
                    'currency_code': 'CAD'
                }
            },
            'total_tax_set': {
                'shop_money': {
                    'amount': '0.00',
                    'currency_code': 'CAD'
                },
                'presentment_money': {
                    'amount': '0.00',
                    'currency_code': 'CAD'
                }
            },
            'total_tip_received': '0.0',
            'admin_graphql_api_id': 'gid://shopify/Order/820982911946154508',
            'line_items': [
                {
                    'id': 866550311766439020,
                    'variant_id': 18052577198170,
                    'title': 'Short sleeve t-shirt',
                    'quantity': 1,
                    'sku': 'aefasfasfsdd-1',
                    'variant_title': None,
                    'vendor': None,
                    'fulfillment_service': 'manual',
                    'product_id': 1995182735450,
                    'requires_shipping': True,
                    'taxable': True,
                    'gift_card': False,
                    'name': 'Short sleeve t-shirt',
                    'variant_inventory_management': 'shopify',
                    'properties': [],
                    'product_exists': True,
                    'fulfillable_quantity': 1,
                    'grams': 1000,
                    'price': '20.00',
                    'total_discount': '0.00',
                    'fulfillment_status': None,
                    'price_set': {
                        'shop_money': {
                            'amount': '20.00',
                            'currency_code': 'CAD'
                        },
                        'presentment_money': {
                            'amount': '20.00',
                            'currency_code': 'CAD'
                        }
                    },
                    'total_discount_set': {
                        'shop_money': {
                            'amount': '0.00',
                            'currency_code': 'CAD'
                        },
                        'presentment_money': {
                            'amount': '0.00',
                            'currency_code': 'CAD'
                        }
                    },
                    'discount_allocations': [],
                    'admin_graphql_api_id': 'gid://shopify/LineItem/866550311766439020',
                    'tax_lines': []
                },
                {
                    'id': 141249953214522974,
                    'variant_id': 31154156109914,
                    'title': 'External Oil FIlter',
                    'quantity': 1,
                    'sku': 'SINSDEOF5906',
                    'variant_title': None,
                    'vendor': None,
                    'fulfillment_service': 'manual',
                    'product_id': 4353136066650,
                    'requires_shipping': True,
                    'taxable': True,
                    'gift_card': False,
                    'name': 'External Oil FIlter',
                    'variant_inventory_management': None,
                    'properties': [],
                    'product_exists': True,
                    'fulfillable_quantity': 1,
                    'grams': 3629,
                    'price': '468.18',
                    'total_discount': '5.00',
                    'fulfillment_status': None,
                    'price_set': {
                        'shop_money': {
                            'amount': '468.18',
                            'currency_code': 'CAD'
                        },
                        'presentment_money': {
                            'amount': '468.18',
                            'currency_code': 'CAD'
                        }
                    },
                    'total_discount_set': {
                        'shop_money': {
                            'amount': '5.00',
                            'currency_code': 'CAD'
                        },
                        'presentment_money': {
                            'amount': '5.00',
                            'currency_code': 'CAD'
                        }
                    },
                    'discount_allocations': [
                        {
                            'amount': '5.00',
                            'discount_application_index': 0,
                            'amount_set': {
                                'shop_money': {
                                    'amount': '5.00',
                                    'currency_code': 'CAD'
                                },
                                'presentment_money': {
                                    'amount': '5.00',
                                    'currency_code': 'CAD'
                                }
                            }
                        }
                    ],
                    'admin_graphql_api_id': 'gid://shopify/LineItem/141249953214522974',
                    'tax_lines': []
                }
            ],
            'shipping_lines': [
                {
                    'id': 271878346596884015,
                    'title': 'Generic Shipping',
                    'price': '10.00',
                    'code': None,
                    'source': 'shopify',
                    'phone': None,
                    'requested_fulfillment_service_id': None,
                    'delivery_category': None,
                    'carrier_identifier': None,
                    'discounted_price': '10.00',
                    'price_set': {
                        'shop_money': {
                            'amount': '10.00',
                            'currency_code': 'CAD'
                        },
                        'presentment_money': {
                            'amount': '10.00',
                            'currency_code': 'CAD'
                        }
                    },
                    'discounted_price_set': {
                        'shop_money': {
                            'amount': '10.00',
                            'currency_code': 'CAD'
                        },
                        'presentment_money': {
                            'amount': '10.00',
                            'currency_code': 'CAD'
                        }
                    },
                    'discount_allocations': [],
                    'tax_lines': []}],
            'billing_address': {
                'first_name': 'Bob',
                'address1': '123 Billing Street',
                'phone': '555-555-BILL',
                'city': 'Billtown',
                'zip': 'K2P0B0',
                'province': 'Kentucky',
                'country': 'United States',
                'last_name': 'Biller',
                'address2': None,
                'company': 'My Company',
                'latitude': None,
                'longitude': None,
                'name': 'Bob Biller',
                'country_code': 'US',
                'province_code': 'KY'
            },
            'shipping_address': {
                'first_name': 'Steve',
                'address1': '123 Shipping Street',
                'phone': '555-555-SHIP',
                'city': 'Shippington',
                'zip': '40003',
                'province': 'Kentucky',
                'country': 'United States',
                'last_name': 'Shipper',
                'address2': None,
                'company': 'Shipping Company',
                'latitude': None,
                'longitude': None,
                'name': 'Steve Shipper',
                'country_code': 'US',
                'province_code': 'KY'
            },
            'fulfillments': [],
            'refunds': [],
            'customer': {
                'id': 115310627314723954,
                'email': 'john@test.com',
                'accepts_marketing': False,
                'created_at': None,
                'updated_at': None,
                'first_name': 'John',
                'last_name': 'Smith',
                'orders_count': 0,
                'state': 'disabled',
                'total_spent': '0.00',
                'last_order_id': None,
                'note': None,
                'verified_email': True,
                'multipass_identifier': None,
                'tax_exempt': False,
                'phone': None,
                'tags': '',
                'last_order_name': None,
                'currency': 'CAD',
                'accepts_marketing_updated_at': None,
                'marketing_opt_in_level': None,
                'admin_graphql_api_id': 'gid://shopify/Customer/115310627314723954',
                'default_address': {
                    'id': 715243470612851245,
                    'customer_id': 115310627314723954,
                    'first_name': None,
                    'last_name': None,
                    'company': None,
                    'address1': '123 Elm St.',
                    'address2': None,
                    'city': 'Ottawa',
                    'province': 'Ontario',
                    'country': 'Canada',
                    'zip': 'K2H7A8',
                    'phone': '123-123-1234',
                    'name': '',
                    'province_code': 'ON',
                    'country_code': 'CA',
                    'country_name': 'Canada',
                    'default': True
                }
            }
        }

    def create(self, validated_data):
        print('hello')
        return {
            'hello': 'hello'
        }

    def save(self, **kwargs):
        print('hi')

