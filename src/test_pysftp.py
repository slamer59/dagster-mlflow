import pysftp

hostname = '127.0.0.1'
username = 'mlflow_user'
password = 'mlflow_pwd'
with pysftp.Connection(hostname, username=username, password=password) as sftp:
    print('ok')
    with sftp.cd(''):             # temporarily chdir to public
        sftp.put('/mlflow/mlflow-artifacts')  # upload file to public/ on remote
        # sftp.get('remote_file')         # get a remote file