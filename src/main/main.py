import csv
import sqlite3

from typing import Literal


# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # You will implement these methods below. They just print TO-DO messages for now.
    load_and_clean_users('../../resources/users.csv')
    load_and_clean_call_logs('../../resources/callLogs.csv')
    write_user_analytics('../../resources/userAnalytics.csv')
    write_ordered_calls('../../resources/orderedCalls.csv')

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# TODO: Implement the following 4 functions. The functions must pass the unit tests to complete the project.


def load_and_clean_csv(
    file_path: str, 
    table: Literal['users', 'callLogs', 'userAnalytics'],
    expected_shape: tuple[tuple[str, type]]
) -> None:
    """Helper function which loads and cleans a csv file to the expected shape"""
    
    # Extracting expected fields and their types
    fields = []
    field_types = []
    
    for field, fieldType in expected_shape:
        fields.append(field)
        field_types.append(fieldType)

    # Final insert statement
    sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES\n"
    added_record = False
    
    # Reading csv file
    try:
        with open(file_path, 'r') as f:
            data = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONE, skipinitialspace=True)

            for i, row in enumerate(data):
                # Skipping rows with too few or too many fields
                if len(row) != len(fields):
                    # print(
                    #     f'{table}: Missing or extra field(s) in row #{i + 1}: ' 
                    #     f'expected {len(fields)} but received {len(row)}'
                    # )
                    continue
                
                # Skips header row
                if i <= 0: continue
                    
                values = '\t('

                # Checks that this field is the expected type
                for field_index, field_value in enumerate(row):
                    # Empty fields auto-fail
                    if len(field_value) <= 0:
                        break

                    expected_type = field_types[field_index]

                    # Numeric types must check if
                    # field_value (which is otherwise always a str )
                    # is a number
                    if expected_type in [int, float]:
                        is_match = field_value.replace('.', '').isdigit()

                    else:
                        is_match = isinstance(field_value, expected_type)

                    if not is_match:
                        # print(
                        #     f'Type mismatch at row #{i + 1} field index {field_index}: '
                        #     f'expected {expected_type} but received {type(field_value)}'
                        # )
                        break

                    # Adding insert values
                    if field_index > 0:
                        values += ', '

                    values += f'"{field_value}"' if expected_type == str else field_value

                # NOTE only happens when loop isn't broken
                else:
                    # print(f'Adding row separator after row #{i + 1}')
                    
                    # Adds separator between records
                    if added_record and i > 1: 
                        sql += ',\n'  

                    sql += values + ')'

                    added_record = True

    except Exception as e:
        # print(f'Unexpected error reading {file_path}: {e}')
        return False
    
    # DEBUG
    # print(f'Final sql statement:\n{sql};')
    
    # Inserting user records
    try:
        cursor.execute(f'{sql};')    

    except Exception as e:
        print(f'Error saving {table} records: {e}')
        return False
    
    return True


# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    load_and_clean_csv(file_path, 'users', (
        ('firstName', str),
        ('lastName', str)
    ))

    # DEBUG
    # cursor.execute('SELECT * FROM users')
    # records = cursor.fetchall()
    # print('\nUsers:')
    # for r in records:
    #     print('\t', r)


# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    load_and_clean_csv(file_path, 'callLogs', (
        ('phoneNumber', str),
        ('startTime', int),
        ('endTime', int),
        ('direction', str),
        ('userId', int)
    ))

    # DEBUG
    # cursor.execute('SELECT * FROM callLogs')
    # records = cursor.fetchall()
    # print('\nCallLogs:')
    # for r in records:
    #     print('\t', r)


# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):
    # Collecting data
    cursor.execute("""
        SELECT userId, AVG(endTime - startTime) as avgDuration, COUNT(*) as numCalls
        FROM callLogs
        GROUP BY userId 
    """)

    data = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    # DEBUG
    # print('\nUserAnalytics:')
    # for r in data:
    #     print('\t', r)

    # Writing to file
    try:
        with open(csv_file_path, 'w') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE)

            # Header row
            writer.writerow(column_names)

            # Data rows
            writer.writerows(data)

    except Exception as e:
        print(f'Unexpected error writing UserAnalytics: {e}')


# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):
    # Collecting data
    cursor.execute("""
        SELECT * from callLogs
        ORDER BY
            userId      ASC,
            startTime   ASC;
    """)

    records = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    try:
        with open(csv_file_path, 'w') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE)

            # Header row
            writer.writerow(column_names)

            # Data row(s)
            writer.writerows(records)

    except Exception as e:
        print(f'Unexpected error writing CallLogs: {e}')


# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()
