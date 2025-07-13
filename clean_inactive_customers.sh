#!/bin/bash

# Clean up inactive customers - customers with no orders in the last year
# This script should be placed in crm/cron_jobs/cleaninactivecustomers.sh

# Get the current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Change to the project directory (adjust path as needed)
cd "$(dirname "$0")/.." || exit 1

# Execute Django management command to delete inactive customers
RESULT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer
from orders.models import Order

# Calculate the cutoff date (1 year ago)
cutoff_date = timezone.now() - timedelta(days=365)

# Find customers with no orders since the cutoff date
inactive_customers = Customer.objects.exclude(
    id__in=Order.objects.filter(
        created_at__gte=cutoff_date
    ).values_list('customer_id', flat=True)
)

# Count and delete inactive customers
deleted_count = inactive_customers.count()
inactive_customers.delete()

print(f'{deleted_count}')
" 2>/dev/null)

# Log the result with timestamp
echo "[$TIMESTAMP] Deleted $RESULT inactive customers" >> /tmp/customercleanuplog.txt

# Exit with appropriate code
if [ $? -eq 0 ]; then
    echo "Customer cleanup completed successfully. Deleted $RESULT customers."
    exit 0
else
    echo "Customer cleanup failed."
    exit 1
fi
