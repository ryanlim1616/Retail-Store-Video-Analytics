#!bin/sh

# ---------------------------------------------------------------------------
#  This job creates a backup of the extracted json file with the timestamp
#  and deletes the original json file at EOD. Then, the job will send the
#  backup json file to the intended destination.
#
# ---------------------------------------------------------------------------



# Obtain date from Rasp pi
date=$(date +%Y%m%d_%H%M%S)

# Feel free to change the naming convention
filename="Backup/data_"$date".txt"

# Create backup
cp data.txt $filename

# Check if files are different (ie: any new addition to the file)
if cmp data.txt $filename
then
# Delete & create new original file if no error
rm data.txt
touch data.txt
else
# return 1 if error
exit 1
fi

# upload using aws
aws s3 cp $filename s3://<backet_name>/
