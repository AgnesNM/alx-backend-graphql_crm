"""
GraphQL Schema for CRM Application
"""

import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from .models import Product


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'


class UpdateLowStockProducts(graphene.Mutation):
    """
    GraphQL Mutation to update low-stock products (stock < 10)
    Increments stock by 10 for products with low stock
    """
    
    class Arguments:
        pass
    
    # Return fields
    updated_products = graphene.List(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    
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
                    message=f"Successfully updated {len(updated_products)} low-stock products"
                )
                
        except Exception as e:
            # Return error response
            return UpdateLowStockProducts(
                updated_products=[],
                success=False,
                message=f"Error updating low-stock products: {str(e)}"
            )


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello World!")
    
    def resolve_hello(self, info):
        return "Hello World!"


class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
