# FSND-capstone
Final Full Stack Nano Degree project

## On MacOS if you installed postgres using Homebrew

```sh
brew services start postgresql
brew services stop postgresql
```

## DB migration

```sh
dropdb calendarapp && createdb calendarapp
rm -rf migrations
flask db init
```
