import happybase

HBASE_SETTINGS = {'host': '127.0.0.1', 'port': '9090'}
CONNECTION = None

def initialize_hbase_connection(host=None, port=None):
    global HBASE_SETTINGS
    if host is None:
        host = HBASE_SETTINGS['host']

    if port is None:
        port = HBASE_SETTINGS['port']

    connection = None
    try:
        connection = happybase.Connection(host, port)
    except Exception as e:
        print e
    return connection

def create_hbase_table(connection, table_name):
    assert hasattr(connection, 'create_table')
    connection.create_table(table_name, {'text': {'max_versions': 1000000000,
                                                  'compression': 'GZ'},
                                         'history': {'max_versions': 1000000000},
                                         'options': {'max_versions': 1000000000}
                                        })

def get_table(table_name):
    global CONNECTION
    connection = CONNECTION
    if connection is None:
        connection = initialize_hbase_connection()
        CONNECTION = connection

    assert hasattr(connection, 'tables')
    if table_name not in connection.tables():
        create_hbase_table(connection, table_name)

    table = connection.table(table_name)
    return table
