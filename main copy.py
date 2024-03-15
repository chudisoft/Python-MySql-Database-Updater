# Use for same table
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
    """ Retrieve table structure from the database """
    table_structure = {}
    cursor = connection.cursor()
    cursor.execute(f"SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_KEY FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{database_name}'")
    
    for (table_name, column_name, column_type, column_key) in cursor:
        if table_name not in table_structure:
            table_structure[table_name] = []
        table_structure[table_name].append((column_name, column_type, column_key))
    
    cursor.close()
    return table_structure

def enclose_identifier(identifier):
    """ Enclose MySQL identifiers with backticks """
    return f"`{identifier}`"

def compare_and_generate_sql(schema_a, schema_b):
    """ Compare two schemas and generate SQL statements """
    sql_statements = []
    
    # Add new tables and columns
    for table, columns in schema_b.items():
        if table not in schema_a:
            # Generate CREATE TABLE statement
            column_definitions = ', '.join([f"{enclose_identifier(name)} {type}" for name, type, _ in columns])
            sql_statements.append(f"CREATE TABLE {enclose_identifier(table)} ({column_definitions});")
        else:
            # Check for new or modified columns
            existing_columns = {name: (type, key) for name, type, key in schema_a[table]}
            for name, type, key in columns:
                if name not in existing_columns:
                    # Add new column
                    sql_statements.append(f"ALTER TABLE {enclose_identifier(table)} ADD COLUMN {enclose_identifier(name)} {type};")
                elif existing_columns[name][0] != type:
                    # Modify existing column
                    sql_statements.append(f"ALTER TABLE {enclose_identifier(table)} MODIFY COLUMN {enclose_identifier(name)} {type};")
    
    # Drop old tables and columns
    for table, columns in schema_a.items():
        if table not in schema_b:
            # Drop table
            sql_statements.append(f"DROP TABLE {enclose_identifier(table)};")
        else:
            existing_columns = {name for name, _, _ in schema_b[table]}
            for name, _, _ in columns:
                if name not in existing_columns:
                    # Drop column
                    sql_statements.append(f"ALTER TABLE {enclose_identifier(table)} DROP COLUMN {enclose_identifier(name)};")
    
    return sql_statements

def main():
    db_a_connection = connect_to_database('smart_business_manager12')
    db_b_connection = connect_to_database('smart_business_manager')

    if db_a_connection and db_b_connection:
        schema_a = get_table_structure(db_a_connection, 'smart_business_manager12')
        schema_b = get_table_structure(db_b_connection, 'smart_business_manager')

        update_statements = compare_and_generate_sql(schema_a, schema_b)

        # Save to sql file
        with open('update_script12.sql', 'w') as file:
            for statement in update_statements:
                file.write(statement + "\n")
            
        db_a_connection.close()
        db_b_connection.close()

if __name__ == "__main__":
    main()
