import mysql.connector
from mysql.connector import Error

def connect_to_database(database):
    """ Connect to a MySQL database """
    try:
        connection = mysql.connector.connect(
            database=database,
            user='root',
            password='',
            host='localhost')
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def get_table_structure(connection, database_name):
    """ Retrieve table structure from the database including nullability and default values """
    table_structure = {}
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_KEY, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{database_name}'
    """)

    for (table_name, column_name, column_type, column_key, is_nullable, column_default) in cursor:
        if table_name not in table_structure:
            table_structure[table_name] = []
        # Append a dictionary for each column
        table_structure[table_name].append({
            'name': column_name,
            'type': column_type,
            'key': column_key,
            'is_nullable': is_nullable,
            'default': column_default
        })

    cursor.close()
    return table_structure


def enclose_identifier(identifier):
    """ Enclose MySQL identifiers with backticks """
    return f"`{identifier}`"

def generate_rename_statements(schema_a, schema_b):
    """ Generate SQL statements for renaming tables """
    rename_statements = []
    for table_a in schema_a:
        if table_a.endswith("table") and table_a[:-5] in schema_b:
            rename_statements.append(f"RENAME TABLE {enclose_identifier(table_a)} TO {enclose_identifier(table_a[:-5])};")
    return rename_statements


def format_column_definition(column):
    """ Format column definition considering type, nullability, and default value. """
    definition = f"{enclose_identifier(column['name'])} {column['type']}"
    if column['is_nullable'] == 'NO':
        definition += ' NOT NULL'
        if column['default'] is not None and column['default'].upper() != 'NULL':
            # Only include the DEFAULT clause for NOT NULL columns if a specific non-NULL default is provided
            definition += f" DEFAULT {format_default_value(column['default'])}"
    # Do not add DEFAULT clause for nullable columns that default to NULL
    return definition

def format_default_value(default):
    """ Format the default value based on its type for SQL statement. """
    if isinstance(default, str) and default.upper() not in ('NULL', 'CURRENT_TIMESTAMP'):
        # Enclose strings in quotes
        return f"'{default}'"
    elif default.upper() == 'CURRENT_TIMESTAMP':
        # CURRENT_TIMESTAMP doesn't get enclosed in quotes
        return default
    else:
        # For numerical values and the keyword NULL
        return default


def compare_and_generate_sql(schema_a, schema_b):
    """ Compare two schemas and generate SQL statements, including column properties """
    sql_statements = ['START TRANSACTION;']
    
    # Add new tables and columns
    for table_b, columns_b in schema_b.items():
        # Find the corresponding table in schema_a
        table_a = next((table_a for table_a in schema_a if table_a.lower() == table_b.lower()), None)

        if table_a is None:
            # If table does not exist in schema_a, create it
            column_definitions = ', '.join([format_column_definition(column) for column in columns_b])
            sql_statements.append(f"CREATE TABLE {enclose_identifier(table_b)} ({column_definitions});")
        else:
            # If table exists, compare columns
            existing_columns_a = {column['name'].lower(): column for column in schema_a[table_a]}
            for column_b in columns_b:
                column_name_b = column_b['name'].lower()
                column_def_b = format_column_definition(column_b)

                if column_name_b not in existing_columns_a:
                    # Add new column
                    sql_statements.append(f"ALTER TABLE {enclose_identifier(table_a)} ADD COLUMN {column_def_b};")
                else:
                    # Check if there are changes in the column definition
                    existing_column = existing_columns_a[column_name_b]
                    column_def_a = format_column_definition(existing_column)
                    if column_def_a.lower() != column_def_b.lower():
                        # Modify existing column with new definition
                        sql_statements.append(f"ALTER TABLE {enclose_identifier(table_a)} MODIFY COLUMN {column_def_b};")

    # Drop old tables and columns not present in schema_b
    for table_a, columns_a in schema_a.items():
        table_b = next((table_b for table_b in schema_b if table_b.lower() == table_a.lower()), None)

        if table_b is None:
            # Drop table if it does not exist in schema_b
            sql_statements.append(f"DROP TABLE {enclose_identifier(table_a)};")
        else:
            # Check for columns to drop
            existing_columns_b = {column['name'].lower() for column in schema_b[table_b]}
            for column_a in columns_a:
                if column_a['name'].lower() not in existing_columns_b:
                    # Drop column if it does not exist in schema_b
                    sql_statements.append(f"ALTER TABLE {enclose_identifier(table_a)} DROP COLUMN {enclose_identifier(column_a['name'])};")
    
    sql_statements.append('COMMIT;')
    return sql_statements



def main():
    db_a_connection = connect_to_database('smart_business_manager123')
    db_b_connection = connect_to_database('smart_business_manager')

    if db_a_connection and db_b_connection:
        schema_a = get_table_structure(db_a_connection, 'smart_business_manager123')
        schema_b = get_table_structure(db_b_connection, 'smart_business_manager')

        # Generate table rename statements
        rename_statements = generate_rename_statements(schema_a, schema_b)

        # Update schema_a after renaming tables
        for statement in rename_statements:
            new_table_name = statement.split("` TO `")[1].rstrip(";`")
            old_table_name = statement.split("` TO `")[0].split("`")[1]
            schema_a[new_table_name] = schema_a.pop(old_table_name)

        update_statements = compare_and_generate_sql(schema_a, schema_b)

        # Save to sql file
        with open('update_script.sql', 'w') as file:
            for statement in rename_statements + update_statements:
                file.write(statement + "\n")
            
        db_a_connection.close()
        db_b_connection.close()

if __name__ == "__main__":
    main()
