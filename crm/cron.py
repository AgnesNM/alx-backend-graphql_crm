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
