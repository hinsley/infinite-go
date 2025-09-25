# Backups

Everything lives in one SQLite file: `data/database.db`. Use the helpers in `scripts/` to copy it safely.

## Take a Backup

- run: `python3 scripts/backup_db.py`
- output: `data/backups/database-YYYYMMDD-HHMMSS.db`
- defaults: keeps 30 newest copies, uses SQLite’s online backup API (no downtime)
- useful flags: `--label smoke-test`, `--retention 7`, `--destination /tmp`

## Schedule Daily Backups

- install: `python3 scripts/setup_backup_cron.py`
- default time: 02:30 server time, logs to `data/backups/backup.log`
- tweak with `--hour`, `--minute`, `--label`, `--retention`, `--log-file`
- confirm with `crontab -l`

## Restore

1. Stop the app.
2. Pick a snapshot in `data/backups/`.
3. Save the current file: `cp data/database.db data/database.db.before-restore`
4. Restore: `cp data/backups/database-YYYYMMDD-HHMMSS.db data/database.db`
5. Restart and verify. Swap the `.before-restore` copy back if needed.

### Notes

- Test restores periodically.
- Copy backups off-box if you need disaster recovery.
- Check `data/backups/backup.log` when cron runs look suspicious.

