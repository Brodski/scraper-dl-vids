
import env_file as env_varz
import MySQLdb

def kickIt(isDebug=False):
    getTodoFromDb()
    return "kicking it"

def getTodoFromDb():
    connection = MySQLdb.connect(
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        db      = env_varz.DATABASE,
        autocommit  = True,
        ssl_mode    = "VERIFY_IDENTITY",
        ssl         = { "ca": "C:/Users/BrodskiTheGreat/Documents/HeidiSQL/cacert-2023-08-22.pem" } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
    )
    
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE Vods
                SET Title = %s,
                    Duration = %s,
                    DurationString = %s,
                    ViewCount = %s,
                    WebpageUrl = %s,
                    UploadDate = FROM_UNIXTIME(%s),
                    Thumbnail = %s,
                    TranscriptStatus = %s
                WHERE Id = %s;
                """
            print("sql")
            print(sql)
            print(values)
            affected_count = cursor.execute(sql, values)
            print(affected_count)
    except Exception as e:
        print(f"Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()
