import strawberry

from app.graphql.mutation import Mutation
from app.graphql.query import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)
