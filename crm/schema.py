"""
GraphQL Schema for CRM Application
"""

import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from .models import Product, Customer, Order


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'


class UpdateLowStockProducts(graphene.Mutation):
    """
    GraphQL Mutation to update low-stock products (stock < 10)
    Increments stock by 10 for products with low stock
    """
    
    class Arguments:
        # No arguments needed for this mutation
        pass
    
    # Return fields
    updated_products = graphene.List(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    updated_count = graphene.Int()
    
    @staticmethod
    def mutate(root, info):
        """
        Execute the mutation to update low-stock products
        """
        try:
            with transaction.atomic():
                # Query products with stock < 10
                low_stock_products = Product.objects.filter(stock__lt=10)
                
                updated_products = []
                
                # Update each low-stock product
                for product in low_stock_products:
                    # Increment stock by 10
                    product.stock += 10
                    product.save()
                    updated_products.append(product)
                
                # Return success response
                return UpdateLowStockProducts(
                    updated_products=updated_products,
                    success=True,
                    message=f"Successfully updated {len(updated_products)} low-stock products",
                    updated_count=len(updated_products)
                )
                
        except Exception as e:
            # Return error response
            return UpdateLowStockProducts(
                updated_products=[],
                success=False,
                message=f"Error updating low-stock products: {str(e)}",
                updated_count=0
            )


class Query(graphene.ObjectType):
    """
    GraphQL Query root
    """
    
    # Hello field for health checks
    hello = graphene.String(default_value="Hello World!")
    
    # Product queries
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID())
    low_stock_products = graphene.List(ProductType, stock_threshold=graphene.Int(default_value=10))
    
    # Customer queries
    all_customers = graphene.List(CustomerType)
    customer = graphene.Field(CustomerType, id=graphene.ID())
    
    # Order queries
    all_orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.ID())
    orders = graphene.List(OrderType, filters=graphene.Argument(graphene.JSONString))
    
    def resolve_all_products(self, info):
        """Resolve all products"""
        return Product.objects.all()
    
    def resolve_product(self, info, id):
        """Resolve single product by ID"""
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_low_stock_products(self, info, stock_threshold):
        """Resolve products with stock below threshold"""
        return Product.objects.filter(stock__lt=stock_threshold)
    
    def resolve_all_customers(self, info):
        """Resolve all customers"""
        return Customer.objects.all()
    
    def resolve_customer(self, info, id):
        """Resolve single customer by ID"""
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_all_orders(self, info):
        """Resolve all orders"""
        return Order.objects.all()
    
    def resolve_order(self, info, id):
        """Resolve single order by ID"""
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None
    
    def resolve_orders(self, info, filters=None):
        """Resolve orders with optional filters"""
        queryset = Order.objects.all()
        
        if filters:
            # Apply date filters if provided
            if 'orderDate_Gte' in filters:
                queryset = queryset.filter(order_date__gte=filters['orderDate_Gte'])
            if 'orderDate_Lte' in filters:
                queryset = queryset.filter(order_date__lte=filters['orderDate_Lte'])
        
        return queryset


class Mutation(graphene.ObjectType):
    """
    GraphQL Mutation root
    """
    
    update_low_stock_products = UpdateLowStockProducts.Field()


# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
