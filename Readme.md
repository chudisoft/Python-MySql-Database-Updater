# Python-MySql-Database-Updater

## Description

The Python-MySQL Database Updater is a sophisticated Python utility tailored to automate the process of transforming and updating the structure of a MySQL database. Ideal for syncing development and production environments or applying version-controlled schema updates, this script ensures that the schema of one database (Database A) is altered to match the schema of another (Database B). It handles table and column renaming, data type modifications, and can apply NOT NULL constraints and default values where specified.

## How it Works

Upon execution, the script connects to two specified MySQL databases: the source (Database A) and the target (Database B). It examines the structure of both, carefully determining the differences. The tool then generates a series of SQL statements to modify Database A's schema—adding, altering, or dropping tables and columns to make it structurally identical to Database B. It wraps the SQL statements in a transaction, ensuring atomicity and consistency: all changes are applied without errors, or none at all.

## Key Features

- **Automated Schema Transformation**: Compares two database schemas and generates SQL statements to transform one to match the other.
- **Safe Operations**: Wraps changes in a transaction to ensure that all modifications are applied reliably.
- **Intelligent Alterations**: Renames tables and columns where necessary, preserving data integrity.
- **Column Property Awareness**: Respects column properties such as data types, NOT NULL constraints, and default values.
- **Nullable Columns**: Correctly handles nullable columns, avoiding setting defaults where not required.

## Installation

To get started with Python-MySql-Database-Updater, ensure you have Python on your system along with `mysql-connector-python` and `mysql-connector` libraries, which can be installed using pip:

```sh
pip install mysql-connector-python mysql-connector
