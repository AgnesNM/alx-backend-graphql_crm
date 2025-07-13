import os
import logging
from datetime import datetime
from celery import shared_task
from django.db import transaction
from django.db.models import Sum
from graphene_django.utils.testing import GraphQLTestCase
import graphene
from graphql import build_client_schema, get_introspection_query
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

# Import your GraphQL schema
from .schema import schema

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
        # GraphQL query to fetch CRM statistics
        query = """
        query {
            customers {
                edges {
                    node {
                        id
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
        
        # Execute the GraphQL query
        request_factory = RequestFactory()
        request = request_factory.post('/graphql/')
        request.user = AnonymousUser()
        
        result = schema.execute(query, context=request)
        
        if result.errors:
            logger.error(f"GraphQL query errors: {result.errors}")
            return "Error: GraphQL query failed"
        
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
        
        # Log to file
        log_file_path = '/tmp/crm_report_log.txt'
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        with open(log_file_path, 'a') as f:
            f.write(report_line)
        
        # Also log to console
        logger.info(f"CRM Report generated: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue")
        
        return f"Report generated successfully: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue"
        
    except Exception as e:
        error_msg = f"Error generating CRM report: {str(e)}"
        logger.error(error_msg)
        
        # Log error to file as well
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_line = f"{timestamp} - ERROR: {error_msg}\n"
        
        try:
            with open('/tmp/crm_report_log.txt', 'a') as f:
                f.write(error_line)
        except:
            pass  # If we can't write to log file, just continue
        
        return error_msg

@shared_task
def generate_crm_report_direct_db():
    """
    Alternative implementation using direct database queries.
    Use this if GraphQL approach has issues.
    """
    try:
        from .models import Customer, Order
        
        # Get statistics directly from database
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(
            total=Sum('totalamount')
        )['total'] or 0
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the report
        report_line = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue.\n"
        
        # Log to file
        log_file_path = '/tmp/crm_report_log.txt'
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        with open(log_file_path, 'a') as f:
            f.write(report_line)
        
        # Also log to console
        logger.info(f"CRM Report generated: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue")
        
        return f"Report generated successfully: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue"
        
    except Exception as e:
        error_msg = f"Error generating CRM report: {str(e)}"
        logger.error(error_msg)
        
        # Log error to file as well
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_line = f"{timestamp} - ERROR: {error_msg}\n"
        
        try:
            with open('/tmp/crm_report_log.txt', 'a') as f:
                f.write(error_line)
        except:
            pass
        
        return error_msg
