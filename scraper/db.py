import happybase

HBASE_SETTINGS = {'host': '127.0.0.1', 'port': '9090'}

def initialize_hbase_connection(host='127.0.0.1', port='9090'):
    connection = None
    try:
        connection = happybase.Connection(host, port)
    except Exception as e:
        print e
    return connection

def create_hbase_table(connection, table_name):
    assert hasattr(connection, 'create_table')
    connection.create_table(table_name, {'text': {'max_versions': -1,
                                                  'compression': 'GZ'},
                                         'history': {'max_versions': -1},
                                         'options': {}
                                        })

def get_table(table_name):
    connection = initialize_hbase_connection()
    assert hasattr(connection, 'tables')
    if table_name not in connection.tables():
        create_hbase_table(connection, table_name)

    table = connection.table(table_name)
    return table
