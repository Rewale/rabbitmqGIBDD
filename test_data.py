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
