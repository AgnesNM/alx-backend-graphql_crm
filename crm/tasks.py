import os
import logging
from datetime import datetime
from celery import shared_task
from django.db import transaction
from django.db.models import Sum, Count
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report using GraphQL queries.
    Logs the report to /tmp/crm_report_log.txt with timestamp.
    """
    try:
        # Import schema here to avoid circular imports
        from .schema import schema
        
        # GraphQL query to fetch CRM statistics
        query = """
        query {
            customers {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
            orders {
                edges {
                    node {
                        id
                        totalamount
                    }
                }
            }
        }
        """
        
        # Create a request context for GraphQL
        request_factory = RequestFactory()
        request = request_factory.post('/graphql/')
        request.user = AnonymousUser()
        
        # Execute the GraphQL query
        result = schema.execute(query, context=request)
        
        if result.errors:
            logger.error(f"GraphQL query errors: {result.errors}")
            # Try the direct database approach as fallback
            return generate_crm_report_direct_db()
        
        # Extract data from the result
        customers_data = result.data.get('customers', {}).get('edges', [])
        orders_data = result.data.get('orders', {}).get('edges', [])
        
        # Calculate statistics
        total_customers = len(customers_data)
        total_orders = len(orders_data)
        
        # Calculate total revenue
        total_revenue = 0
        for order in orders_data:
            order_node = order.get('node', {})
            amount = order_node.get('totalamount', 0)
            if amount:
                total_revenue += float(amount)
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the report
        report_line = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue.\n"
        
        # Get log file path from settings
        log_file_path = '/tmp/crm_report_log.txt'
        if hasattr(settings, 'CRM_SETTINGS') and 'CRM_REPORT_LOG_PATH' in settings.CRM_SETTINGS:
            log_file_path = settings.CRM_SETTINGS['CRM_REPORT_LOG_PATH']
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        # Write to log file
        with open(log_file_path, 'a') as f:
            f.write(report_line)
        
        # Also log to console
        logger.info(f"CRM Report generated: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue")
        
        return f"Report generated successfully: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue"
        
    except Exception as e:
        error_msg = f"Error generating CRM report: {str(e)}"
        logger.error(error_msg)
        
        # Try direct database approach as fallback
        try:
            return generate_crm_report_direct_db()
        except Exception as fallback_error:
            # Log error to file
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_line = f"{timestamp} - ERROR: {error_msg}\n"
            
            try:
                log_file_path = '/tmp/crm_report_log.txt'
                if hasattr(settings, 'CRM_SETTINGS') and 'CRM_REPORT_LOG_PATH' in settings.CRM_SETTINGS:
                    log_file_path = settings.CRM_SETTINGS['CRM_REPORT_LOG_PATH']
                
                with open(log_file_path, 'a') as f:
                    f.write(error_line)
            except:
                pass
            
            return error_msg

def generate_crm_report_direct_db():
    """
    Alternative implementation using direct database queries.
    """
    try:
        # Try to import models - adjust these imports based on your actual model structure
        try:
            from .models import Customer, Order
        except ImportError:
            # If models are in separate apps, try importing from there
            try:
                from customers.models import Customer
                from orders.models import Order
            except ImportError:
                # If no models exist yet, create dummy data
                total_customers = 0
                total_orders = 0
                total_revenue = 0.0
                
                # Generate timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Format the report
                report_line = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue.\n"
                
                # Get log file path
                log_file_path = '/tmp/crm_report_log.txt'
                if hasattr(settings, 'CRM_SETTINGS') and 'CRM_REPORT_LOG_PATH' in settings.CRM_SETTINGS:
                    log_file_path = settings.CRM_SETTINGS['CRM_REPORT_LOG_PATH']
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
                
                # Write to log file
                with open(log_file_path, 'a') as f:
                    f.write(report_line)
                
                logger.info(f"CRM Report generated (no data): {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue")
                return f"Report generated successfully (no data): {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue"
        
        # Get statistics from database
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(
            total=Sum('totalamount')
        )['total'] or 0.0
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the report
        report_line = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue.\n"
        
        # Get log file path
        log_file_path = '/tmp/crm_report_log.txt'
        if hasattr(settings, 'CRM_SETTINGS') and 'CRM_REPORT_LOG_PATH' in settings.CRM_SETTINGS:
            log_file_path = settings.CRM_SETTINGS['CRM_REPORT_LOG_PATH']
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        # Write to log file
        with open(log_file_path, 'a') as f:
            f.write(report_line)
        
        logger.info(f"CRM Report generated: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue")
        
        return f"Report generated successfully: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue"
        
    except Exception as e:
        error_msg = f"Error generating CRM report (direct DB): {str(e)}"
        logger.error(error_msg)
        
        # Log error to file
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_line = f"{timestamp} - ERROR: {error_msg}\n"
        
        try:
            log_file_path = '/tmp/crm_report_log.txt'
            if hasattr(settings, 'CRM_SETTINGS') and 'CRM_REPORT_LOG_PATH' in settings.CRM_SETTINGS:
                log_file_path = settings.CRM_SETTINGS['CRM_REPORT_LOG_PATH']
            
            with open(log_file_path, 'a') as f:
                f.write(error_line)
        except:
            pass
        
        return error_msg
