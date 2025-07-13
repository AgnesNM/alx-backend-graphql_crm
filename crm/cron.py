"""
Django-crontab heartbeat logger for CRM application health monitoring.
"""

import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Log heartbeat message to confirm CRM application health.
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    Also optionally queries GraphQL hello field to verify endpoint responsiveness.
    """
    # Generate timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Base heartbeat message
    heartbeat_message = f"{timestamp} CRM is alive"
    
    # Optional GraphQL health check
    graphql_status = check_graphql_endpoint()
    if graphql_status:
        heartbeat_message += f" - GraphQL endpoint responsive: {graphql_status}"
    else:
        heartbeat_message += " - GraphQL endpoint not responsive"
    
    # Log to file
    try:
        with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
            log_file.write(heartbeat_message + "\n")
    except Exception as e:
        # Fallback logging if file write fails
        print(f"Error writing heartbeat log: {e}")


def check_graphql_endpoint():
    """
    Query GraphQL hello field to verify endpoint responsiveness.
    Returns the hello message if successful, None if failed.
    """
    try:
        # GraphQL endpoint
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Simple hello query
        query = gql("""
            query {
                hello
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        return result.get("hello", "Unknown response")
        
    except Exception as e:
        # Return None if GraphQL query fails
        return None


def update_low_stock():
    """
    Execute GraphQL mutation to update low-stock products (stock < 10)
    and log the updates to file.
    """
    try:
        # GraphQL endpoint
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL mutation for updating low-stock products
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    updatedProducts {
                        id
                        name
                        stock
                    }
                    success
                    message
                    updatedCount
                }
            }
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        mutation_result = result.get("updateLowStockProducts", {})
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        
        # Prepare log entry
        log_entry = f"[{timestamp}] Low Stock Update: "
        
        if mutation_result.get("success"):
            updated_products = mutation_result.get("updatedProducts", [])
            updated_count = mutation_result.get("updatedCount", 0)
            
            log_entry += f"Successfully updated {updated_count} products\n"
            
            # Log each updated product
            for product in updated_products:
                product_name = product.get("name", "Unknown")
                new_stock = product.get("stock", 0)
                log_entry += f"  - {product_name}: Stock updated to {new_stock}\n"
        else:
            error_message = mutation_result.get("message", "Unknown error")
            log_entry += f"Failed - {error_message}\n"
        
        # Write to log file
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(log_entry)
            
    except Exception as e:
        # Log error if mutation fails
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        error_entry = f"[{timestamp}] Low Stock Update Error: {str(e)}\n"
        
        try:
            with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
                log_file.write(error_entry)
        except:
            print(f"Error logging low stock update failure: {e}")
