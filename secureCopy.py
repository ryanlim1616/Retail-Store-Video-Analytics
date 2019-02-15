# ---------------------------------------------------------------------------
#  This job creates a backup of the extracted json file with the timestamp
#  and deletes the original json file at EOD. Then, the job will send the
#  backup json file to the intended destination.
#
# ---------------------------------------------------------------------------

from subprocess import check_output, CalledProcessError
import boto3


# Obtain date from Rasp pi
date = subprocess.check_output(["date", "+%Y%m%d_%H%M%S"])

# Feel free to change the naming convention
filename = "Backup/" + "data_" + date.strip().decode('ascii') + ".txt"

# Create backup
cmd = check_output(["cp", "data.txt", filename])

# Check if files are different (ie: any new addition to the file)
nfilename = "."+filename
try:
    cmd = check_output(["cmp", "data.txt", nfilename])
except CalledProcessError as e:
    raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

# Delete & create new original file if no error
cmd = check_output(["rm", "data.txt"])
cmd = check_output(["touch", "data.txt"])

# create new s3 client
s3 = boto3.client('s3')

# set bucket_name
bucket_name = '<bucket_name>'

# upload json file to s3 bucket
s3.upload_file(filename, bucket_name, filename)
