import cx_Oracle
import config
cx_Oracle.init_oracle_client(lib_dir="instantclient_19_8")

connection = cx_Oracle.connect(user=config.username, password=config.password, dsn=config.dsn)

cursor = connection.cursor()

cursor.execute("""begin
                     execute immediate 'drop table pytab';
                     exception when others then if sqlcode <> -942 then raise; end if;
                  end;""")
cursor.execute("create table pytab (id number, data varchar2(20))")

