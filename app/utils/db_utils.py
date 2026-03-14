# app/database.py - Extended configuration


def calculate_pool_settings(
    expected_concurrent_requests: int,
    db_max_connections: int = 100,
) -> dict:
    """
    Calculate optimal pool settings based on expected load.

    PostgreSQL default max_connections is usually 100.
    Leave room for admin connections and other services.
    """
    # Reserve 20% of connections for admin and monitoring
    available_connections = int(db_max_connections * 0.8)

    # Base pool size handles average load
    pool_size = min(expected_concurrent_requests // 2, available_connections // 2)
    pool_size = max(pool_size, 5)  # Minimum 5 connections

    # Overflow handles traffic spikes
    max_overflow = min(pool_size, available_connections - pool_size)

    return {
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    }


# Example: Configure for 200 concurrent requests with 100 max DB connections
pool_config = calculate_pool_settings(
    expected_concurrent_requests=200,
    db_max_connections=100,
)

# Result: pool_size=40, max_overflow=40
