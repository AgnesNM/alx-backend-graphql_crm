#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def main():
    # GraphQL endpoint
    endpoint = "http://localhost:8000/graphql"
    
    # Calculate the date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Create GraphQL client
    transport = RequestsHTTPTransport(url=endpoint)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # GraphQL query to find pending orders within the last 7 days
    query = gql('''
        query GetPendingOrders($startDate: String!) {
            pendingOrders(orderDateAfter: $startDate) {
                id
                orderDate
                customer {
                    email
                }
                status
            }
        }
    ''')
    
    try:
        # Execute the query
        result = client.execute(query, variable_values={"startDate": seven_days_ago})
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Process the results
        orders = result.get('pendingOrders', [])
        
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Processing {len(orders)} pending orders\n")
            
            for order in orders:
                order_id = order['id']
                customer_email = order['customer']['email']
                order_date = order['orderDate']
                
                # Log the order reminder
                log_entry = f"[{timestamp}] Order ID: {order_id}, Customer: {customer_email}, Order Date: {order_date}\n"
                log_file.write(log_entry)
        
        # Print success message to console
        print("Order reminders processed!")
        
    except Exception as e:
        # Log any errors
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] ERROR: {str(e)}\n")
        
        print(f"Error processing order reminders: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
