# CRM GraphQL Application with Celery

This is a Django-based CRM application with GraphQL API and Celery task scheduling for automated report generation.

## Features

- GraphQL API for customers and orders
- Automated weekly CRM report generation
- Celery task scheduling with Redis broker
- Logging to `/tmp/crm_report_log.txt`

## Setup Instructions

### 1. Install Dependencies

First, install Redis (required for Celery broker):

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

#### On macOS (using Homebrew):
```bash
brew install redis
brew services start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

#### On Windows:
Download and install Redis from the official website or use Windows Subsystem for Linux (WSL).

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Your project is configured to use SQLite (as seen in your settings.py). Run migrations to set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create the SQLite database file (`db.sqlite3`) and the necessary tables including those for Celery Beat scheduling.

### 4. Verify Celery Configuration

Test that Celery can find your tasks:

```bash
celery -A crm inspect registered
```

This should list your `crm.tasks.generate_crm_report` task.

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start the Application

#### Terminal 1: Start Django Development Server
```bash
python manage.py runserver
```

#### Terminal 2: Start Celery Worker
```bash
celery -A crm worker --loglevel=info
```

#### Terminal 3: Start Celery Beat (Task Scheduler)
```bash
celery -A crm beat --loglevel=info
```

### 7. Verify Setup

1. **Test Redis Connection**: 
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Test Celery Task Discovery**:
   ```bash
   celery -A crm inspect registered
   # Should list: crm.tasks.generate_crm_report
   ```

3. **Test GraphQL API**: Visit `http://localhost:8000/graphql/` to access the GraphQL interface

4. **Check Celery Tasks**: The worker terminal should show task execution logs

5. **Verify Report Generation**: Check `/tmp/crm_report_log.txt` for generated reports

## Testing the Report Generation

### Manual Task Execution

You can manually trigger the report generation task:

```bash
python manage.py shell
```

Then in the Django shell:
```python
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
```

### Check Logs

View the generated reports:
```bash
cat /tmp/crm_report_log.txt
```

### Scheduled Execution

The task is scheduled to run every Monday at 6:00 AM UTC. You can modify the schedule in `settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

For testing purposes, you can change it to run more frequently:
```python
# Run every minute for testing
'schedule': crontab(minute='*'),
```

## GraphQL Queries

### Example Queries

#### Get All Customers
```graphql
query {
  customers {
    edges {
      node {
        id
        name
        email
        phone
      }
    }
  }
}
```

#### Get All Orders
```graphql
query {
  orders {
    edges {
      node {
        id
        customer {
          name
        }
        totalamount
        orderdate
      }
    }
  }
}
```

## Monitoring

### Celery Monitoring

You can monitor Celery tasks using Flower:

```bash
pip install flower
celery -A crm flower
```

Then visit `http://localhost:5555` to see the Flower monitoring interface.

### Log Files

- **CRM Reports**: `/tmp/crm_report_log.txt`
- **Celery Worker**: Console output from worker terminal
- **Celery Beat**: Console output from beat terminal

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is installed and running
   - Check if Redis is accessible on `localhost:6379`

2. **Database Connection Error**
   - Your project uses SQLite by default, so this should work out of the box
   - If you encounter issues, make sure the database file has proper permissions

3. **GraphQL Query Errors**
   - Ensure you have some test data in the database
   - Check if the schema is properly configured

4. **Task Not Running**
   - Verify both Celery worker and beat are running
   - Check the task schedule in `settings.py`

### Debug Commands

Check Redis connection:
```bash
redis-cli ping
```

Check Celery worker status:
```bash
celery -A crm inspect active
```

Check scheduled tasks:
```bash
celery -A crm inspect scheduled
```

## File Structure

```
crm/
├── __init__.py          # Celery app initialization
├── celery.py           # Celery configuration
├── settings.py         # Django settings with Celery config
├── tasks.py            # Celery tasks
├── schema.py           # GraphQL schema
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## Development

### Adding New Tasks

To add new Celery tasks, create them in `crm/tasks.py`:

```python
@shared_task
def my_new_task():
    # Task implementation
    pass
```

### Scheduling New Tasks

Add new scheduled tasks to `CELERY_BEAT_SCHEDULE` in `settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'my-new-task': {
        'task': 'crm.tasks.my_new_task',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
```

## Production Deployment

For production deployment:

1. Use a production-grade Redis server
2. Configure proper logging
3. Use process managers like Supervisor or systemd
4. Set up monitoring and alerting
5. Configure proper security settings

## License

This project is for educational purposes.
