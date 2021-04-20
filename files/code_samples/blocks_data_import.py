import requests
import sqlite3
from sqlite3 import Error
import time


def create_connection(dbName):
    """
    Create a database connection to the sqlite database
    specified by dbName
    :param dbName: database file name
    :return connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(dbName)
    except Error as e:
        print(e)
    
    return conn


def update_block_data(dbName):
    """
    opens database, find last block No. in database, then create a http request to get last block 
    data, finally missed blocks data is acquired from website and update the database
    :param dbName: database file name
    :return: void
    """
    conn = create_connection(dbName)
    dbLastBlock = get_last_block_no(conn)
    latestBlockNo = get_latest_block()
    # print(dbLastBlock)
    update_database(conn, dbLastBlock + 1, latestBlockNo)


def get_blocks_at_date(year, month, day):
    base_url = "http://chain.api.btc.com/v3/block/date/"
    url = base_url + "{0}{1}{2}".format(year, str(month).zfill(2), str(day).zfill(2))
    print(url)
    response = requests.get(url)
    while response.status_code != 200:
        print(response.status_code)
        time.sleep(0.1)
        response = requests.get(url)
    data_list = response.json()['data']
    for block in data_list:
        id = block['height']
        timestamp = block['timestamp']
        pool_name = block['extras']['pool_name']
        print("test 2020 / 12 / 15 => {0}".format(id))

get_blocks_at_date(2020, 12, 15)


def update_database(conn, first, last):
    """
    add block data for total range between first and last block IDs to the database
    :param conn: database connection object
    :param first: first block ID to acquire data
    :param last: last block ID to acquire data
    :return: ID of the last block added to the database
    """
    baseUrl = "http://chain.api.btc.com/v3/block/"
    for index in range(first, last + 1):
        print("index = ", index)
        try:
            url = baseUrl + str(index)
            response = requests.get(url)
            while response.status_code != 200:
                print(response.status_code)
                # time.sleep(0.1)
                response = requests.get(url)
            data = response.json()['data']
            blockId = data['height']
            timeStamp = data['timestamp']
            poolName = data['extras']['pool_name']
            add_single_block_data(conn, blockId, timeStamp, poolName)
        except Error as e:
            print(e)
            return index - 1
    return last
        
  
def add_single_block_data(conn, blockId, timeStamp, poolName):
    """
    add single record including block ID, timestamp and pool name to the database
    :param conn: database connection object
    :param blockId: ID of the block
    :param timestamp: The time when the block is solved
    :param poolName: name of the solver pool
    :return: void
    """
    cursor = conn.cursor()
    sql = """INSERT INTO blocks (blockId, timeStamp, poolName) VALUES (?,?,?);"""
    data = (blockId, timeStamp, poolName)
    cursor.execute(sql, data)
    conn.commit()
    # cursor.close()
    
    
    
def get_latest_block():
    """
    send a http request to get latest block No
    :return: latest block No in block-chain network
    """
    baseUrl = "http://chain.api.btc.com/v3/block/latest"
    response = requests.get(baseUrl)
    while response.status_code != 200:
        # print(response.status_code)
        time.sleep(5)
        response = requests.get(baseUrl)
    data = response.json()
    data = data['data']
    height = data['height']
    return height
    
    
def get_last_block_no(conn):
    """
    using database connection, get heighest block ID
    :param conn: database connection
    :return: highest block No in database
    """
    cur = conn.cursor()
    sql = "SELECT blockId FROM blocks ORDER BY blockId DESC LIMIT 1"
    cur.execute(sql)
    rows = cur.fetchall()
    if len(rows) > 0:
        return rows[0][0]
    else:
        return 0
    
    
def main():
    databaseName = "database.db"
    update_block_data(databaseName)
    
    
    
if __name__ == '__main__':
    main()