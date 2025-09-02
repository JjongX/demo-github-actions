# macrogen-assistant cron

## Clear remaining chat files (`remove_chat_files.sh`)
Make the script executable:
```
$ chmod +x ~/macrogen-assistant/remove_chat_files.sh
```

Set up a cron job to delete the remaining files daily at 00:02.
```
$ crontab -e
```

Add the following cron job:
```
0 0 * * * /home/ubuntu/remove_chat_files.sh >> /home/ubuntu/cron.log 2>&1
```

Then check that the job is set:
```
$ crontab -l
```