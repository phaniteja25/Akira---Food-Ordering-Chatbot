import mysql.connector

global cnx
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="phanitejau",
    database = "pandeyji_eatery"
)


def get_order_status(order_id:int):
    cursor = cnx.cursor()

    query = ("SELECT status from order_tracking WHERE order_id = %s")

    cursor.execute(query,(order_id,))

    result  = cursor.fetchone()

    cursor.close()


    if result is not None:
        return result[0]
    else:
        return None


def get_next_order_id():
    cursor = cnx.cursor()

    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    if result is None:
        return 1
    else:
        return result+1


def insert_food_item(food_item,quantity,order_id):

    try:
        cursor = cnx.cursor()

        #calling the stored procedure

        cursor.callproc('insert_order_item',(food_item,quantity,order_id))

        cnx.commit()

        #closing the cursor

        cursor.close()

        print("Order item inserted successfully")

        return 1
    
    except mysql.connector.Error as err:
        print(f"Error inserting order item :  {err}")

        #rollback changes if necessary

        cnx.rollback()

        return -1
def get_total_price(order_id):

    cursor = cnx.cursor()

    query =f"SELECT get_total_order_price({order_id})"

    cursor.execute(query)

    #fetching the result

    result = cursor.fetchone()[0]

    #closing the cursor

    cursor.close()

    return result


def insert_order_tracking(order_id,status):
    cursor = cnx.cursor()

    insert_query = "INSERT INTO order_tracking (order_id,status) VALUES (%s,%s)"
    cursor.execute(insert_query,(order_id,status))

    cnx.commit()

    cursor.close()
    







