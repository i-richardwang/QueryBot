"""
Milvus vector database service module.

Provides unified Milvus database operation functionality, including collection creation,
data insertion, vector search, etc.
"""

import asyncio
from typing import Dict, Any, List
from pymilvus import (
    Collection,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType
)

from utils.core.logging_config import get_logger

logger = get_logger(__name__)


def create_milvus_collection(collection_config: Dict[str, Any], dim: int) -> Collection:
    """
    Create Milvus collection with support for multiple vector fields and create indexes for vector fields.

    Args:
        collection_config (Dict[str, Any]): Collection configuration.
        dim (int): Vector dimension.

    Returns:
        Collection: Created Milvus collection object.
    """
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    ]
    for field in collection_config["fields"]:
        fields.append(
            FieldSchema(name=field["name"], dtype=DataType.VARCHAR, max_length=65535)
        )
        if field.get("is_vector", False):
            fields.append(
                FieldSchema(
                    name=f"{field['name']}_vector", dtype=DataType.FLOAT_VECTOR, dim=dim
                )
            )

    schema = CollectionSchema(fields, collection_config["description"])
    collection = Collection(collection_config["name"], schema)

    # Create indexes for vector fields
    for field in collection.schema.fields:
        if field.name.endswith("_vector"):
            index_params = {
                "metric_type": "IP",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024},
            }
            collection.create_index(field.name, index_params)

    collection.load()
    logger.info(f"Successfully created and loaded collection: {collection_config['name']}")
    return collection


def insert_to_milvus(
    collection: Collection,
    data: List[Dict[str, Any]],
    vectors: Dict[str, List[List[float]]],
):
    """
    Insert data into Milvus collection with support for multiple vector fields.

    Args:
        collection (Collection): Milvus collection object.
        data (List[Dict[str, Any]]): Data to insert, each dictionary represents a row of data.
        vectors (Dict[str, List[List[float]]]): Corresponding vector data, key is field name, value is vector list.
    """
    entities = []
    for field in collection.schema.fields:
        if field.name not in ["id"] and not field.name.endswith("_vector"):
            entities.append([d.get(field.name) for d in data])
        elif field.name.endswith("_vector"):
            original_field_name = field.name[:-7]  # Remove "_vector" suffix
            entities.append(vectors.get(original_field_name, []))

    collection.insert(entities)
    collection.load()
    logger.info(f"Successfully inserted {len(data)} records into collection {collection.name}")


def update_milvus_records(
    collection: Collection,
    data: List[Dict[str, Any]],
    vectors: Dict[str, List[List[float]]],
    embedding_fields: List[str],
):
    """
    Update records in Milvus collection with support for multiple vector fields. If record doesn't exist, insert new record.

    Args:
        collection (Collection): Milvus collection object.
        data (List[Dict[str, Any]]): Data to update, each dictionary represents a row of data.
        vectors (Dict[str, List[List[float]]]): Corresponding vector data, key is field name, value is vector list.
        embedding_fields (List[str]): List of field names used to generate vectors.
    """
    for record in data:
        # Build query expression using all embedding_fields
        query_expr = " && ".join(
            [f"{field} == '{record[field]}'" for field in embedding_fields]
        )
        existing_records = collection.query(
            expr=query_expr,
            output_fields=["id"],
        )

        if existing_records:
            # Update existing record
            collection.delete(expr=f"id in {[r['id'] for r in existing_records]}")

        # Insert record (whether new record or updated record)
        entities = []
        for field in collection.schema.fields:
            if field.name not in ["id"] and not field.name.endswith("_vector"):
                entities.append([record.get(field.name)])
            elif field.name.endswith("_vector"):
                original_field_name = field.name[:-7]  # Remove "_vector" suffix
                entities.append([vectors[original_field_name][data.index(record)]])

        collection.insert(entities)

    collection.load()
    logger.info(f"Successfully updated {len(data)} records in collection {collection.name}")


def search_in_milvus(
    collection: Collection, query_vector: List[float], vector_field: str, top_k: int = 1
) -> List[Dict[str, Any]]:
    """
    Search for most similar vectors in Milvus collection.

    Args:
        collection (Collection): Milvus collection object.
        query_vector (List[float]): Query vector.
        vector_field (str): Vector field name to search.
        top_k (int): Number of most similar results to return. Default is 1.

    Returns:
        List[Dict[str, Any]]: Search results list.
    """
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

    output_fields = [
        field.name
        for field in collection.schema.fields
        if not field.name.endswith("_vector") and field.name != "id"
    ]

    results = collection.search(
        data=[query_vector],
        anns_field=f"{vector_field}_vector",
        param=search_params,
        limit=top_k,
        output_fields=output_fields,
    )

    search_results = [
        {
            **{field: getattr(hit.entity, field) for field in output_fields},
            "distance": hit.distance,
        }
        for hit in results[0]
    ]

    logger.debug(f"Found {len(search_results)} results in collection {collection.name}")
    return search_results


async def asearch_in_milvus(
    collection: Collection, query_vector: List[float], vector_field: str, top_k: int = 1
) -> List[Dict[str, Any]]:
    """
    Asynchronously search for most similar vectors in Milvus collection.

    Args:
        collection (Collection): Milvus collection object.
        query_vector (List[float]): Query vector.
        vector_field (str): Vector field name to search.
        top_k (int): Number of most similar results to return. Default is 1.

    Returns:
        List[Dict[str, Any]]: Search results list.
    """
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

    output_fields = [
        field.name
        for field in collection.schema.fields
        if not field.name.endswith("_vector") and field.name != "id"
    ]

    # Use asyncio.to_thread to run synchronous operation in thread
    results = await asyncio.to_thread(
        collection.search,
        data=[query_vector],
        anns_field=f"{vector_field}_vector",
        param=search_params,
        limit=top_k,
        output_fields=output_fields,
    )

    search_results = [
        {
            **{field: getattr(hit.entity, field) for field in output_fields},
            "distance": hit.distance,
        }
        for hit in results[0]
    ]

    logger.debug(f"Async search found {len(search_results)} results in collection {collection.name}")
    return search_results


def get_collection_stats(collection: Collection) -> Dict[str, Any]:
    """
    Get collection statistics.

    Args:
        collection (Collection): Milvus collection object.

    Returns:
        Dict[str, Any]: Dictionary containing collection statistics.
    """
    stats = {
        "entity_count": collection.num_entities,
        "field_count": len(collection.schema.fields) - 1,  # Subtract auto-generated id field
        "index_type": collection.index().params.get("index_type", "unknown"),
    }
    logger.debug(f"Retrieved collection {collection.name} statistics: {stats}")
    return stats