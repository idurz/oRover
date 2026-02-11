# Systemd service
While writing the oRover system, we realized that we want an easy way to start oRover directly after starting the host controller. Systemd is designed to start services, control them and are able to restart them automatic.

  * Create the following file: 

```
sudo /etc/systemd/system/orover.service
```

  * In below code part Change the <USERID> and </path/to/orover> to your needs   
  * Add the following content

```
[Unit]
Description=oRover - Object Recognition and Versatile Exploration Robot
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
StartLimitBurst=5
StartLimitIntervalSec=10
User=<USERID>
ExecStart=/usr/bin/python3 </path/to/orover>/launcher.py

[Install]
WantedBy=multi-user.target
```

That’s it. We can now start the service:

```
systemctl start orover
```
And automatically get it to start on boot:

```
systemctl enable orover
```