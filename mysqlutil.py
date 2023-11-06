import mysql.connector
from setting import Setting


class MysqlUtil:
    connection = None

    case_table_name = 'anjian'

    company_table_name = 'company'

    share_holder_table_name = 'shareholder'

    @staticmethod
    def connect():
        MysqlUtil.__create_database_if_need()

        MysqlUtil.connection = mysql.connector.connect(
            host=Setting.get().mysql.host,
            port=Setting.get().mysql.port,
            user=Setting.get().mysql.user,
            password=Setting.get().mysql.password,
            database=Setting.get().mysql.database
        )

        if not MysqlUtil.connection.is_connected():
            print('failed to connect the mysql server')
            return False
        else:
            return True

    @staticmethod
    def __create_database_if_need():
        # Establish a connection to the MySQL server
        conn = mysql.connector.connect(
            host=Setting.get().mysql.host,
            port=Setting.get().mysql.port,
            user=Setting.get().mysql.user,
            password=Setting.get().mysql.password,
        )

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Check if the database exists
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        database_exists = False

        for database in databases:
            if database[0] == Setting.get().mysql.database:
                database_exists = True
                break

        # Create the "qcc" database if it doesn't exist
        if not database_exists:
            cursor.execute("CREATE DATABASE {}".format(Setting.get().mysql.database))
            print("Database {} created successfully.".format(Setting.get().mysql.database))

        # Close the cursor and connection
        cursor.close()
        conn.close()

    @staticmethod
    def create_table_if_need():
        # Check if the connection is successful
        if MysqlUtil.connection is None or not MysqlUtil.connection.is_connected():
            print("not connected to MySQL database")
            return False

        # Create a cursor object for executing SQL statements
        cursor = MysqlUtil.connection.cursor()

        # Define the CREATE TABLE statement
        create_case_table_query = """
            CREATE TABLE IF NOT EXISTS {} (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                case_id VARCHAR(40),
                judgment_debtor VARCHAR(40),
                judgment_creditor VARCHAR(40),
                unfulfilled_amount VARCHAR(40),
                executing_court VARCHAR(80),
                finality_date VARCHAR(20)
            )
        """.format(MysqlUtil.case_table_name)

        create_company_table_query = """
                    CREATE TABLE IF NOT EXISTS {} (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        company_id VARCHAR(40),
                        name VARCHAR(100),
                        phone_number VARCHAR(240),
                        lr VARCHAR(240),
                        region VARCHAR(100),
                        rc VARCHAR(40),
                        pc VARCHAR(40),
                        status VARCHAR(40)
                    )
        """.format(MysqlUtil.company_table_name)

        create_shareholder_table_query = """
                            CREATE TABLE IF NOT EXISTS {} (
                                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                                company_id VARCHAR(40),
                                name VARCHAR(100),
                                rate VARCHAR(40)
                            )
        """.format(MysqlUtil.share_holder_table_name)

        # Execute the CREATE TABLE statement
        cursor.execute(create_case_table_query)
        cursor.execute(create_company_table_query)
        cursor.execute(create_shareholder_table_query)

        # Commit the transaction
        MysqlUtil.connection.commit()

        # Close the cursor and connection
        cursor.close()

        return True

    @staticmethod
    def insert_case(case):
        # Check if the connection is successful
        if MysqlUtil.connection is None or not MysqlUtil.connection.is_connected():
            print("not connected to MySQL database")
            return False

        # Create a cursor object for executing SQL statements
        cursor = MysqlUtil.connection.cursor()

        # Define the DELETE statement
        delete_query = """
            DELETE FROM {}
            WHERE case_id = %s
        """.format(MysqlUtil.case_table_name)
        delete_data = case.case_id

        # Define the INSERT statement
        insert_query = """
            INSERT INTO {} (case_id, judgment_debtor, judgment_creditor, unfulfilled_amount, executing_court, finality_date) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """.format(MysqlUtil.case_table_name)
        insert_data = (case.case_id, case.judgment_debtor, case.judgment_creditor, case.unfulfilled_amount, case.executing_court, case.finality_date)

        # Execute the SQL statement
        cursor.execute(delete_query, delete_data)
        cursor.execute(insert_query, insert_data)

        # Commit the transaction
        MysqlUtil.connection.commit()

        # Close the cursor
        cursor.close()

        return True

    @staticmethod
    def insert_company(company):
        # Check if the connection is successful
        if MysqlUtil.connection is None or not MysqlUtil.connection.is_connected():
            print("not connected to MySQL database")
            return False

        # Create a cursor object for executing SQL statements
        cursor = MysqlUtil.connection.cursor()

        # Define the DELETE statement
        delete_share_holder_query = """
                    DELETE FROM {}
                    WHERE company_id = %s
                """.format(MysqlUtil.share_holder_table_name)
        delete_share_holder_data = company.company_id
        delete_company_query = """
                            DELETE FROM {}
                            WHERE company_id = %s
                        """.format(MysqlUtil.company_table_name)
        delete_company_data = company.company_id

        # Define the INSERT statement
        insert_share_holder_query = """
                    INSERT INTO {} (company_id, name, rate) 
                    VALUES (%s, %s, %s)
                    """.format(MysqlUtil.share_holder_table_name)
        insert_company_query = """
                            INSERT INTO {} (company_id, name, phone_number, lr, region, rc, pc, status) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """.format(MysqlUtil.company_table_name)
        insert_company_data = (company.company_id, company.company_name, company.phone_number, company.lr, company.region, company.rc, company.pc, company.status)

        # Execute the SQL statement
        cursor.execute(delete_share_holder_query, delete_share_holder_data)
        cursor.execute(delete_company_query, delete_company_data)
        for item in company.share_holders:
            insert_share_holder_data = (item.company_id, item.name, item.rate)
            cursor.execute(insert_share_holder_query, insert_share_holder_data)
        cursor.execute(insert_company_query, insert_company_data)

        # Commit the transaction
        MysqlUtil.connection.commit()

        # Close the cursor
        cursor.close()
