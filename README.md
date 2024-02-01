# python-mysql-backup

Simple example to make a MySQL backup with Python.

## Prerequisites
[Install Python3](https://www.python.org/downloads/)


## Usage
1. Clone the repo
```
git clone https://github.com/ttiverson3/python-mysql-backup.git
cd python-mysql-backup
```
2. Fill database config to db.ini

Here is an example:
```
[service_name]
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_db
DB_USER=root
DB_PWD=root
BACKUP_PATH=backup
IGNORE_TABLE=your_db.table_name
```

3. Run make-database-backup.py
```
python3 make-database-backup.py service_name backup_type file_limit

Arguments:
    service_name     Name of the service
    backup_type      Type of the backup: part or all. ("part" will exclude the table specified in the "IGNORE_TABLE" section of the ini file.)
    file_limit       maximum number of the files in backup folder
```