test_schema_rpc = {
    'GIBDDFINESPROGR': {
        'AMQP': {
            'config': {
                'address': '192.168.0.216',
                'port': 5672,
                'username': 'guest',
                'password': 'guest',
                'exchange': 'gibddExchange',
                'quenue': 'gibddfinesQueue',
                'virtualhost': '/',
                'timeout': 30000
            },
            'methods': {
                'write': {
                    'fines': {
                        'sts': ['str', 10, True],
                        'gov_number': ['str', 9, True]
                    }

                }
            }
        }

    },
    'SendService': {
        'AMQP': {
            'config': {
                'address': '192.168.0.216',
                'port': 5672,
                'username': 'guest',
                'password': 'guest',
                'exchange': 'sendExchange',
                'quenue': 'sendQueue',
                'virtualhost': '/',
                'timeout': 30000
            },
            'methods': {
                # 'write': {
                #     'test_method': {
                #         'test_str': ['str', 32, True]
                #     }
                #
                # }
            }
        }

    }

}
test_parse_penalty_result = [
    [
        {
            "name": "Дата и время нарушения:",
            "value": "26.08.2018 в 23:30"
        },
        {
            "name": "Статья КоАП РФ:",
            "value": "12.26 ч.1 - невыполнение водителем законного требования сотрудника полиции о прохождении медицинского освидетельствования на состояние опьянения"
        },
        {
            "name": "Подразделение ГИБДД:",
            "value": "ОГИБДД и ДПС ОМВД России по г. Анапе"
        },
        {
            "name": "Постановление:",
            "value": "18810423180170013454 от 18.09.2018"
        },
        {
            "name": "Сумма штрафа:",
            "value": "30000 руб."
        }
    ],
    [
        {
            "name": "Дата и время нарушения:",
            "value": "20.03.2022 в 17:46"
        },
        {
            "name": "Статья КоАП РФ:",
            "value": "12.9 ч.2 - превышение установленной скорости движения транспортного средства на величину более 20, но не более 40 км/ч"
        },
        {
            "name": "Подразделение ГИБДД:",
            "value": "ЦАФАПОДД ГИБДД (дислокация г. Краснодар) ГУ МВД России по Краснодарскому краю"
        },
        {
            "name": "Постановление:",
            "value": "18810523220404075459 от 04.04.2022"
        },
        {
            "name": "Сумма штрафа:",
            "value": "500 руб.\nдо 25.04.2022 скидка 250 руб."
        }
    ]
]

test_parse_registation_histoty = {
    'registration_history': {
        "vehicle_brand_or_model": "Test model",
        "model_product_year": "2004",
        "vin_code": "Z8T4D5FS9EM013865",
        "chasis_number": "-",
        "body_number": "Z8T4D5FS9EM013865",
        "color": "БЕЛЫЙ",
        "working_volume": "1598.0",
        "power": "90.000/122.0",
        "vehicle_type": "Легковые автомобили седан",
        "periods_of_vehicle_ownership": [
            "c 18.04.2014 по 24.05.2014: Физическое лицо",
            "c 24.05.2014 по 24.10.2014: Физическое лицо",
        ],
    }
}

test_parse_restriction_history = {
    'restrictions_history': [{

        "venhicle_model": "Нет данных",
        "model_product_year": "2004 г.",
        "restriction_date": "13.07.2018 г.",
        "restriction_initiator_region": "Томская область",
        "restricted_by": "Судебный пристав",
        "restriction_type": "Запрет на регистрационные действия",
        "reason": "Причина",
        "initiators_phone": "73424322312",
        "gibdd_key": "70#SP23364643"
    }]
}

test_parse_wanted_history = {
    'wanted_history': [{
        "venhicle_model": "Нет данных",
        "model_product_year": "2004 г.",
        "registration_of_wanted_date": "12.03.2021",
        "region_of_initiator": "город Москва"
    }]
}
