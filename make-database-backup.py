#!/usr/bin/python

import os, time, sys, subprocess, configparser

def check_dir_exist(backup_dir):
	if os.path.isdir(backup_dir) == False:
		try:
			os.makedirs(backup_dir)
		except Exception as e:
			exit(e)
	return True

def check_file_count_limit(file_path, file_limit):
	dir_list = os.listdir(file_path)
	
	if len(dir_list) == 0:
		exit(f"There are no files in the '{file_path}'")
	else:
		sorted_dir_list = sorted(dir_list,  key = lambda x: os.path.getmtime(os.path.join(file_path, x)))

	count_file = len(sorted_dir_list)
	if count_file <= file_limit:
		return True
	else:
		os.remove(f"{file_path}/{sorted_dir_list[0]}")
		del sorted_dir_list[0]
		return check_file_count_limit(file_path, file_limit)

def backup_databse(backup_type):
	format_time = get_time_format()
	filename = f"{db_name}_{format_time}.sql"
	backup_file_path = f"{backup_dir}/{filename}"

	try:
		if backup_type == "part":
			mysqldump_cmd = f"mysqldump -h {db_host} -P {db_port} -u {db_user} -p{db_pwd} {db_name} --ignore-table={ignore_table} --result-file={backup_file_path}"
		elif backup_type == "all":
			mysqldump_cmd = f"mysqldump -h {db_host} -P {db_port} -u {db_user} -p{db_pwd} {db_name} --result-file={backup_file_path}"
	except (NameError) as e:
		error_msg = f"[{service}]: {e}"
		exit(error_msg)
	
	# make .sql file
	process1 = subprocess.Popen(mysqldump_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stderr = process1.communicate()[1]
	return_code = process1.wait()
	if return_code != 0:
		subprocess.Popen(["rm", backup_file_path])
		exit(stderr.decode())

	# do file compression
	process2 = subprocess.Popen(f"gzip {backup_file_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stderr = process2.communicate()[1]
	return_code = process2.wait()
	if return_code != 0:
		subprocess.Popen(["rm", f"{backup_file_path}.gz"])
		exit(stderr.decode())

	return True

def get_time_format():
	now = int(time.time())
	time_array = time.localtime(now)
	format_time = time.strftime("%Y_%m_%d_%H_%M_%S", time_array)
	return format_time

if __name__ == "__main__":
	try:
		service = sys.argv[1]
		backup_type = sys.argv[2]
		file_limit = int(sys.argv[3])
	except (IndexError) as e:
		print("Usage: python make-database-part.backup.py service_name backup_type file_limit")
		print("Arguments:")
		print("  service_name     Name of the service")
		print("  backup_type      Type of the backup: part or all")
		print("  file_limit       maximum number of the files in backup folder")
		exit()
	
	backup_type_allow_list = ["part", "all"]
	if backup_type not in backup_type_allow_list:
		exit("backup_type should be 'part' or 'all'")

	current_path = os.getcwd()
	config = configparser.ConfigParser()
	config.read(f"{current_path}/db.ini")
	for key, value in config.items(service):
		# db_host, db_port, db_name, db_user, db_pwd, backup_path
		if (key == "ignore_table"):
			if (backup_type == "part"):
				ignore_table = value
				if (value == ""):
					error_msg = f"{current_path}/db.ini: '{key.upper()}' is empty for [{service}]"
					exit(error_msg)
		else:
			locals()[key] = value
			if (value == ""):
				error_msg = f"{current_path}/db.ini: '{key.upper()}' is empty for [{service}]"
				exit(error_msg)
	
	backup_args = ['db_host', 'db_port', 'db_name', 'db_user', 'db_pwd', 'backup_path']
	for arg in backup_args:
		if arg not in locals():
			error_msg = f"{current_path}/db.ini: '{arg.upper()}' not set for [{service}]"
			exit(error_msg)
	

	backup_dir = f"{backup_path}/{service}/{backup_type}"
	check_dir_exist(backup_dir)

	backup_result = backup_databse(backup_type)

	check_file_count_limit(backup_dir, file_limit)

	if backup_result:
		print("success")
		sys.exit(0)
