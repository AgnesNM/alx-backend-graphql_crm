#!/usr/bin/env python3
"""
GraphQL-based Order Reminder Script
Queries pending orders from the last 7 days and logs reminders.
"""

import sys
import os
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def get_pending_orders():
    """
    Query GraphQL endpoint for orders with order_date within the last 7 days
    """
    # GraphQL endpoint
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    date_filter = seven_days_ago.strftime("%Y-%m-%d")
    
    # GraphQL query for pending orders within last 7 days
    query = gql("""
        query GetPendingOrders($dateFilter: String!) {
            orders(filters: { orderDate_Gte: $dateFilter }) {
                id
                orderDate
                customer {
                    email
                }
            }
        }
    """)
    
    try:
        # Execute the query
        result = client.execute(query, variable_values={"dateFilter": date_filter})
        return result.get("orders", [])
    except Exception as e:
        print(f"Error querying GraphQL endpoint: {e}")
        return []

def log_order_reminder(order_id, customer_email):
    """
    Log order reminder to file with timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}\n"
    
    try:
        with open("/tmp/order_reminders_log.txt", "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def main():
    """
    Main function to process order reminders
    """
    try:
        # Get pending orders from GraphQL
        pending_orders = get_pending_orders()
        
        if not pending_orders:
            print("No pending orders found within the last 7 days.")
            return
        
        # Process each order
        for order in pending_orders:
            order_id = order.get("id")
            customer_email = order.get("customer", {}).get("email")
            
            if order_id and customer_email:
                log_order_reminder(order_id, customer_email)
            else:
                print(f"Warning: Incomplete order data for order {order_id}")
        
        print("Order reminders processed!")
        
    except Exception as e:
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
