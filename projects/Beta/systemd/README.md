# Alpha Heartbeat - systemd Configuration

These files configure the periodic heartbeat that wakes Alpha for Project Beta.

## Files

- **alpha-heartbeat.service** - The service unit (what to run)
- **alpha-heartbeat.timer** - The timer unit (when to run it)
- **wake-alpha.sh** - The wrapper script that actually invokes Claude

## Installation on the Pi

```bash
# Copy the service and timer to systemd
sudo cp alpha-heartbeat.service /etc/systemd/system/
sudo cp alpha-heartbeat.timer /etc/systemd/system/

# Copy the wake script to Alpha-Home and make it executable
cp wake-alpha.sh /home/jefferyharrell/Projects/Alpha-Home/
chmod +x /home/jefferyharrell/Projects/Alpha-Home/wake-alpha.sh

# Create the logs directory
mkdir -p /home/jefferyharrell/Projects/Alpha-Home/logs

# Reload systemd to pick up the new files
sudo systemctl daemon-reload

# Edit the timer to enable your desired schedule
sudo nano /etc/systemd/system/alpha-heartbeat.timer

# Enable and start the timer
sudo systemctl enable alpha-heartbeat.timer
sudo systemctl start alpha-heartbeat.timer
```

## Useful Commands

```bash
# Check timer status and next fire time
systemctl list-timers alpha-heartbeat.timer

# View heartbeat logs
journalctl -u alpha-heartbeat.service

# Or the raw log file
tail -f /home/jefferyharrell/Projects/Alpha-Home/logs/heartbeat.log

# Manually trigger a heartbeat (for testing)
sudo systemctl start alpha-heartbeat.service

# Stop the timer
sudo systemctl stop alpha-heartbeat.timer

# Disable (won't start on reboot)
sudo systemctl disable alpha-heartbeat.timer
```

## Timer Configuration Options

Edit `/etc/systemd/system/alpha-heartbeat.timer` to change the schedule.

**For a one-night test (Dec 10, 3am-3:50am):**
```ini
OnCalendar=2025-12-10 03:00,03:10,03:20,03:30,03:40,03:50:00
```

**For every night at 3am:**
```ini
OnCalendar=*-*-* 03:00,03:10,03:20,03:30,03:40,03:50:00
```

**For testing every 10 minutes all day:**
```ini
OnCalendar=*:00,10,20,30,40,50
```

After editing, run:
```bash
sudo systemctl daemon-reload
sudo systemctl restart alpha-heartbeat.timer
```

## Notes

- `Persistent=false` means missed heartbeats won't run retroactively if the Pi was off
- `RandomizedDelaySec=30` adds up to 30 seconds of jitter to avoid exact-second firing
- Logs go to both journald and `/home/jefferyharrell/Projects/Alpha-Home/logs/heartbeat.log`
