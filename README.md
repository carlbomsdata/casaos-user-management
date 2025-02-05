# Update!!

In collaboration with BigBearCasaOS there's now a more user friendly was to handle multiple users. 
Please see https://community.bigbeartechworld.com/t/added-bigbearcasaos-user-management-to-bigbearcasaos/2227

# CasaOS User Management Script

A Python script for managing CasaOS users directly in the `user.db` database. Features include:

- Listing users
- Adding new users
- Editing user passwords
- Removing users
- Resetting the database

**Note**: Requires `sudo` permissions and Python 3.x. Always backs up the database before making changes.

### Run the script with:
```bash
sudo python3 program.py
```

### Or install as a System Command:
```bash
sudo cp program.py /usr/bin/casaos-users-manager
sudo chmod +x /usr/bin/casaos-users-manager
```
And run with
```
sudo casaos-users-manager
```

### Or build for your platform using pyinstaller:
```bash
pip install pyinstaller
```
```bash
pyinstaller --onefile program.py
```
Make a copy of the script from the ./dist folder and then run:
```bash
sudo ./program
```
