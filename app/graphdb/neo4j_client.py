from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver
from app.core.config import settings
from app.core.logging import logger


class Neo4jClient:
    """
    Neo4j graph database client with connection pooling, parameterized query execution,
    and graceful offline fallback.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        self.uri = uri or settings.NEO4J_URI
        self.username = username or settings.NEO4J_USERNAME
        self.password = password or settings.NEO4J_PASSWORD
        self.enabled = enabled if enabled is not None else settings.ENABLE_NEO4J
        self._driver: Optional[Driver] = None

    def connect(self) -> bool:
        if not self.enabled or not self.uri or not self.username:
            logger.info("Neo4j integration is disabled or credentials not provided. Using offline fallback.")
            return False

        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                connection_timeout=5.0
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j graph database at {self.uri}")
            return True
        except Exception as e:
            logger.warning(f"Neo4j connection could not be established ({e}). Falling back to in-memory graph mode.")
            self._driver = None
            return False

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a parameterized Cypher query. Never concatenates raw parameters into Cypher.
        """
        if self._driver is None:
            if not self.connect():
                return []

        try:
            with self._driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error executing Cypher query: {e}")
            return []
