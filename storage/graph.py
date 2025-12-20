"""
Associative Memory Graph
Graph-based storage for associative memory and relationship mapping.
"""

from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import sqlite3
import asyncio
import json
from collections import defaultdict, deque
from loguru import logger

from storage.persistence import PersistenceManager


class NodeType(Enum):
    """Types of nodes in the associative graph"""
    MEMORY = "memory"
    CONCEPT = "concept"
    EVENT = "event"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    TEMPORAL = "temporal"


class EdgeType(Enum):
    """Types of edges in the associative graph"""
    SIMILARITY = "similarity"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    HIERARCHICAL = "hierarchical"
    ASSOCIATIVE = "associative"
    SEQUENTIAL = "sequential"


class RelationshipStrength(Enum):
    """Relationship strength levels"""
    WEAK = 0.2
    MODERATE = 0.5
    STRONG = 0.8
    VERY_STRONG = 1.0


@dataclass
class GraphNode:
    """Represents a node in the associative graph"""
    id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at


@dataclass
class GraphEdge:
    """Represents an edge in the associative graph"""
    source_id: str
    target_id: str
    edge_type: EdgeType
    strength: float
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0


@dataclass
class GraphPath:
    """Represents a path through the graph"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_strength: float
    path_length: int


@dataclass
class GraphSearchResult:
    """Result from graph search"""
    node: GraphNode
    path: GraphPath
    relevance_score: float
    search_depth: int


class GraphStore:
    """
    Associative Memory Graph Store
    
    Provides graph-based associative memory:
    - Node and edge management
    - Path finding and traversal
    - Community detection
    - Centrality analysis
    - Graph algorithms for memory retrieval
    """
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.persistence_manager = persistence_manager
        
        # In-memory graph representation
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[Tuple[str, str], GraphEdge] = {}  # (source, target) -> edge
        
        # Graph indices for fast lookup
        self.outgoing_edges: Dict[str, List[str]] = defaultdict(list)  # node_id -> [target_ids]
        self.incoming_edges: Dict[str, List[str]] = defaultdict(list)  # node_id -> [source_ids]
        self.node_index: Dict[str, Set[str]] = defaultdict(set)  # property_key -> {node_ids}
        self.edge_index: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # edge_type -> [(source, target)]
        
        # Graph statistics and metrics
        self.graph_stats = {
            "total_nodes": 0,
            "total_edges": 0,
            "search_operations": 0,
            "path_finding_operations": 0,
            "community_detection_operations": 0
        }
        
        # Performance settings
        self.max_path_length = 10
        self.min_edge_strength = 0.1
        self.max_search_results = 100
    
    async def initialize(self):
        """Initialize the graph store"""
        logger.info("🕸️ Initializing associative graph store...")
        
        try:
            # Load existing graph from database
            await self._load_graph()
            
            # Build indices
            await self._build_indices()
            
            logger.info(f"✅ Graph store initialized with {len(self.nodes)} nodes and {len(self.edges)} edges")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize graph store: {e}")
            raise
    
    async def create_node(
        self, 
        node_type: NodeType, 
        label: str, 
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new node in the graph
        
        Args:
            node_type: Type of the node
            label: Human-readable label
            properties: Node properties
            
        Returns:
            Node ID
        """
        try:
            node_id = f"node_{len(self.nodes)}_{datetime.now().timestamp()}"
            
            node = GraphNode(
                id=node_id,
                node_type=node_type,
                label=label,
                properties=properties or {}
            )
            
            # Add to memory
            self.nodes[node_id] = node
            
            # Update indices
            await self._update_node_indices(node)
            
            # Persist to database
            await self._persist_node(node)
            
            logger.debug(f"Created node {node_id} of type {node_type.value}")
            return node_id
            
        except Exception as e:
            logger.error(f"Error creating node: {e}")
            raise
    
    async def create_edge(
        self, 
        source_id: str, 
        target_id: str, 
        edge_type: EdgeType, 
        strength: float,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create an edge between two nodes
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of the edge
            strength: Edge strength (0.0 to 1.0)
            properties: Edge properties
            
        Returns:
            True if successful
        """
        try:
            # Validate nodes exist
            if source_id not in self.nodes:
                raise ValueError(f"Source node {source_id} does not exist")
            if target_id not in self.nodes:
                raise ValueError(f"Target node {target_id} does not exist")
            
            # Create edge
            edge = GraphEdge(
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type,
                strength=strength,
                properties=properties or {}
            )
            
            # Add to memory
            edge_key = (source_id, target_id)
            self.edges[edge_key] = edge
            
            # Update indices
            self.outgoing_edges[source_id].append(target_id)
            self.incoming_edges[target_id].append(source_id)
            self.edge_index[edge_type.value].append((source_id, target_id))
            
            # Update node index for properties
            await self._update_node_indices(self.nodes[source_id])
            await self._update_node_indices(self.nodes[target_id])
            
            # Persist to database
            await self._persist_edge(edge)
            
            logger.debug(f"Created edge {source_id} -> {target_id} of type {edge_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating edge: {e}")
            return False
    
    async def find_connected_nodes(
        self, 
        node_id: str, 
        edge_types: Optional[List[EdgeType]] = None,
        min_strength: float = None,
        max_depth: int = 1
    ) -> List[GraphSearchResult]:
        """
        Find nodes connected to a given node
        
        Args:
            node_id: Starting node ID
            edge_types: Types of edges to follow
            min_strength: Minimum edge strength
            max_depth: Maximum search depth
            
        Returns:
            List of connected nodes with paths
        """
        try:
            self.graph_stats["search_operations"] += 1
            
            if node_id not in self.nodes:
                raise ValueError(f"Node {node_id} does not exist")
            
            results = []
            visited = set()
            queue = deque([(node_id, 0, [])])  # (node_id, depth, path)
            
            while queue:
                current_id, depth, path = queue.popleft()
                
                if current_id in visited or depth > max_depth:
                    continue
                
                visited.add(current_id)
                
                # Get outgoing edges
                for target_id in self.outgoing_edges.get(current_id, []):
                    edge_key = (current_id, target_id)
                    if edge_key in self.edges:
                        edge = self.edges[edge_key]
                        
                        # Filter by edge type and strength
                        if edge_types and edge.edge_type not in edge_types:
                            continue
                        if min_strength and edge.strength < min_strength:
                            continue
                        
                        # Create path
                        target_node = self.nodes[target_id]
                        new_path = path + [current_id]
                        
                        # Calculate relevance score
                        relevance_score = self._calculate_relevance_score(edge, depth)
                        
                        # Create search result
                        graph_path = GraphPath(
                            nodes=[self.nodes[nid] for nid in new_path + [target_id]],
                            edges=[self.edges[(new_path[i], new_path[i+1])] for i in range(len(new_path)-1)],
                            total_strength=edge.strength,
                            path_length=depth + 1
                        )
                        
                        result = GraphSearchResult(
                            node=target_node,
                            path=graph_path,
                            relevance_score=relevance_score,
                            search_depth=depth + 1
                        )
                        
                        results.append(result)
                        
                        # Continue search if not at max depth
                        if depth + 1 < max_depth:
                            queue.append((target_id, depth + 1, new_path))
            
            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            logger.debug(f"Found {len(results)} connected nodes from {node_id}")
            return results[:self.max_search_results]
            
        except Exception as e:
            logger.error(f"Error finding connected nodes: {e}")
            raise
    
    async def find_shortest_path(
        self, 
        source_id: str, 
        target_id: str, 
        edge_types: Optional[List[EdgeType]] = None,
        max_length: int = None
    ) -> Optional[GraphPath]:
        """
        Find shortest path between two nodes using Dijkstra's algorithm
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_types: Types of edges to consider
            max_length: Maximum path length
            
        Returns:
            Shortest path or None if no path exists
        """
        try:
            self.graph_stats["path_finding_operations"] += 1
            
            if source_id not in self.nodes:
                raise ValueError(f"Source node {source_id} does not exist")
            if target_id not in self.nodes:
                raise ValueError(f"Target node {target_id} does not exist")
            
            max_length = max_length or self.max_path_length
            
            # Dijkstra's algorithm for shortest path
            distances = {source_id: 0}
            previous = {}
            unvisited = set(self.nodes.keys())
            unvisited.remove(source_id)
            
            while unvisited:
                # Find unvisited node with minimum distance
                current = min(unvisited, key=lambda node: distances.get(node, float('inf')))
                current_distance = distances[current]
                
                if current == target_id or current_distance > max_length:
                    break
                
                unvisited.remove(current)
                
                # Check all neighbors
                for neighbor_id in self.outgoing_edges.get(current, []):
                    if neighbor_id in unvisited:
                        edge_key = (current, neighbor_id)
                        if edge_key in self.edges:
                            edge = self.edges[edge_key]
                            
                            # Filter by edge type
                            if edge_types and edge.edge_type not in edge_types:
                                continue
                            
                            # Calculate new distance (inverse of edge strength)
                            edge_distance = 1.0 - edge.strength
                            new_distance = current_distance + edge_distance
                            
                            if new_distance < distances.get(neighbor_id, float('inf')):
                                distances[neighbor_id] = new_distance
                                previous[neighbor_id] = current
            
            # Reconstruct path
            if target_id not in distances:
                return None  # No path found
            
            path_nodes = []
            path_edges = []
            current = target_id
            
            while current != source_id:
                path_nodes.append(self.nodes[current])
                if current in previous:
                    prev = previous[current]
                    edge_key = (prev, current)
                    if edge_key in self.edges:
                        path_edges.append(self.edges[edge_key])
                    current = prev
                else:
                    break
            
            path_nodes.append(self.nodes[source_id])
            path_nodes.reverse()
            path_edges.reverse()
            
            # Calculate total strength (minimum edge strength in path)
            total_strength = min(edge.strength for edge in path_edges) if path_edges else 1.0
            
            return GraphPath(
                nodes=path_nodes,
                edges=path_edges,
                total_strength=total_strength,
                path_length=len(path_nodes)
            )
            
        except Exception as e:
            logger.error(f"Error finding shortest path: {e}")
            raise
    
    async def detect_communities(self, method: str = "louvain") -> Dict[str, List[str]]:
        """
        Detect communities in the graph
        
        Args:
            method: Community detection method
            
        Returns:
            Dictionary mapping community IDs to node IDs
        """
        try:
            self.graph_stats["community_detection_operations"] += 1
            
            if method == "louvain":
                return await self._louvain_community_detection()
            elif method == "label_propagation":
                return await self._label_propagation_community_detection()
            elif method == "connected_components":
                return await self._connected_components_detection()
            else:
                raise ValueError(f"Unsupported community detection method: {method}")
                
        except Exception as e:
            logger.error(f"Error detecting communities: {e}")
            raise
    
    async def get_node_centrality(self, node_id: str) -> Dict[str, float]:
        """
        Calculate centrality metrics for a node
        
        Args:
            node_id: Node ID
            
        Returns:
            Dictionary of centrality metrics
        """
        try:
            if node_id not in self.nodes:
                raise ValueError(f"Node {node_id} does not exist")
            
            node = self.nodes[node_id]
            
            # Degree centrality
            degree = len(self.outgoing_edges[node_id]) + len(self.incoming_edges[node_id])
            degree_centrality = degree / max(1, len(self.nodes) - 1)
            
            # Betweenness centrality (simplified)
            betweenness_centrality = await self._calculate_betweenness_centrality(node_id)
            
            # Closeness centrality (simplified)
            closeness_centrality = await self._calculate_closeness_centrality(node_id)
            
            return {
                "degree_centrality": degree_centrality,
                "betweenness_centrality": betweenness_centrality,
                "closeness_centrality": closeness_centrality,
                "total_connections": degree
            }
            
        except Exception as e:
            logger.error(f"Error calculating centrality for node {node_id}: {e}")
            raise
    
    async def search_nodes(
        self, 
        query: str,
        node_types: Optional[List[NodeType]] = None,
        property_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[GraphSearchResult]:
        """
        Search for nodes based on label and properties
        
        Args:
            query: Search query
            node_types: Filter by node types
            property_filters: Filter by properties
            limit: Maximum number of results
            
        Returns:
            List of matching nodes
        """
        try:
            results = []
            
            for node_id, node in self.nodes.items():
                score = 0.0
                
                # Filter by node type
                if node_types and node.node_type not in node_types:
                    continue
                
                # Calculate label match score
                if query.lower() in node.label.lower():
                    score += 1.0
                
                # Calculate property match scores
                property_matches = 0
                if property_filters:
                    for key, value in property_filters.items():
                        if key in node.properties and node.properties[key] == value:
                            property_matches += 1
                    
                    if property_filters:
                        score += property_matches / len(property_filters)
                
                if score > 0:
                    # Create a simple path (single node)
                    path = GraphPath(
                        nodes=[node],
                        edges=[],
                        total_strength=1.0,
                        path_length=1
                    )
                    
                    result = GraphSearchResult(
                        node=node,
                        path=path,
                        relevance_score=score,
                        search_depth=0
                    )
                    
                    results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            logger.debug(f"Found {len(results)} nodes matching query '{query}'")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching nodes: {e}")
            raise
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        
        # Calculate basic metrics
        node_types_count = defaultdict(int)
        edge_types_count = defaultdict(int)
        
        for node in self.nodes.values():
            node_types_count[node.node_type.value] += 1
        
        for edge in self.edges.values():
            edge_types_count[edge.edge_type.value] += 1
        
        # Calculate connectivity metrics
        connected_components = await self._get_connected_components()
        largest_component_size = max(len(component) for component in connected_components) if connected_components else 0
        
        # Calculate average metrics
        avg_degree = sum(len(self.outgoing_edges[node_id]) + len(self.incoming_edges[node_id]) 
                        for node_id in self.nodes) / max(1, len(self.nodes))
        
        avg_edge_strength = sum(edge.strength for edge in self.edges.values()) / max(1, len(self.edges))
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types_count),
            "edge_types": dict(edge_types_count),
            "connected_components": len(connected_components),
            "largest_component_size": largest_component_size,
            "average_degree": avg_degree,
            "average_edge_strength": avg_edge_strength,
            "density": len(self.edges) / max(1, len(self.nodes) * (len(self.nodes) - 1)),
            **self.graph_stats
        }
    
    def _calculate_relevance_score(self, edge: GraphEdge, depth: int) -> float:
        """Calculate relevance score for search result"""
        
        # Base score from edge strength
        base_score = edge.strength
        
        # Reduce score with depth (farther nodes are less relevant)
        depth_penalty = 1.0 / (1.0 + depth)
        
        # Boost score for certain edge types
        edge_type_boost = {
            EdgeType.SIMILARITY: 1.1,
            EdgeType.CAUSAL: 1.2,
            EdgeType.TEMPORAL: 1.1,
            EdgeType.HIERARCHICAL: 1.0,
            EdgeType.ASSOCIATIVE: 1.0,
            EdgeType.SEQUENTIAL: 1.1
        }
        
        boost = edge_type_boost.get(edge.edge_type, 1.0)
        
        return base_score * depth_penalty * boost
    
    async def _louvain_community_detection(self) -> Dict[str, List[str]]:
        """Simplified Louvain community detection"""
        
        # This is a simplified implementation
        # In practice, you would use a proper graph library like NetworkX
        
        communities = {}
        node_to_community = {}
        
        # Initialize each node as its own community
        for node_id in self.nodes.keys():
            communities[node_id] = [node_id]
            node_to_community[node_id] = node_id
        
        # Simple community merging based on edge strength
        improved = True
        while improved:
            improved = False
            
            for node_id in self.nodes.keys():
                current_community = node_to_community[node_id]
                best_community = current_community
                best_gain = 0
                
                # Try moving to neighboring communities
                for neighbor_id in self.outgoing_edges.get(node_id, []):
                    neighbor_community = node_to_community[neighbor_id]
                    
                    if neighbor_community != current_community:
                        # Calculate modularity gain (simplified)
                        gain = self._calculate_modularity_gain(
                            node_id, current_community, neighbor_community
                        )
                        
                        if gain > best_gain:
                            best_gain = gain
                            best_community = neighbor_community
                
                # Move node if improvement found
                if best_community != current_community and best_gain > 0:
                    communities[current_community].remove(node_id)
                    communities[best_community].append(node_id)
                    node_to_community[node_id] = best_community
                    improved = True
        
        # Remove empty communities
        communities = {k: v for k, v in communities.items() if v}
        
        return communities
    
    async def _label_propagation_community_detection(self) -> Dict[str, List[str]]:
        """Label propagation community detection"""
        
        # Initialize labels
        labels = {node_id: node_id for node_id in self.nodes.keys()}
        
        # Iterative label propagation
        max_iterations = 100
        for iteration in range(max_iterations):
            changed = False
            nodes_shuffled = list(self.nodes.keys())
            
            # Shuffle node order for random tie-breaking
            import random
            random.shuffle(nodes_shuffled)
            
            for node_id in nodes_shuffled:
                # Count labels in neighborhood
                label_counts = defaultdict(int)
                
                # Check incoming and outgoing edges
                for neighbor_id in self.incoming_edges.get(node_id, []) + self.outgoing_edges.get(node_id, []):
                    neighbor_label = labels[neighbor_id]
                    label_counts[neighbor_label] += 1
                
                if label_counts:
                    # Find most frequent label
                    most_frequent_label = max(label_counts.items(), key=lambda x: x[1])[0]
                    
                    if most_frequent_label != labels[node_id]:
                        labels[node_id] = most_frequent_label
                        changed = True
            
            if not changed:
                break
        
        # Group nodes by label
        communities = defaultdict(list)
        for node_id, label in labels.items():
            communities[label].append(node_id)
        
        return dict(communities)
    
    async def _connected_components_detection(self) -> List[List[str]]:
        """Find connected components using BFS"""
        
        visited = set()
        components = []
        
        for node_id in self.nodes.keys():
            if node_id not in visited:
                component = []
                queue = deque([node_id])
                
                while queue:
                    current = queue.popleft()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)
                        
                        # Add neighbors to queue
                        for neighbor in self.outgoing_edges.get(current, []) + self.incoming_edges.get(current, []):
                            if neighbor not in visited:
                                queue.append(neighbor)
                
                components.append(component)
        
        return components
    
    async def _calculate_betweenness_centrality(self, node_id: str) -> float:
        """Calculate betweenness centrality (simplified)"""
        
        # Simplified betweenness centrality calculation
        # In practice, use proper graph algorithms
        
        total_shortest_paths = 0
        paths_through_node = 0
        
        source_nodes = list(self.nodes.keys())
        target_nodes = list(self.nodes.keys())
        
        for source in source_nodes:
            for target in target_nodes:
                if source != target and source != node_id and target != node_id:
                    path = await self.find_shortest_path(source, target)
                    if path and node_id in [n.id for n in path.nodes]:
                        paths_through_node += 1
                    total_shortest_paths += 1
        
        return paths_through_node / max(1, total_shortest_paths)
    
    async def _calculate_closeness_centrality(self, node_id: str) -> float:
        """Calculate closeness centrality"""
        
        # Calculate sum of shortest path lengths from node to all other nodes
        total_distance = 0
        reachable_nodes = 0
        
        for other_id in self.nodes.keys():
            if other_id != node_id:
                path = await self.find_shortest_path(node_id, other_id)
                if path:
                    total_distance += path.path_length
                    reachable_nodes += 1
        
        if reachable_nodes > 0:
            return reachable_nodes / total_distance
        else:
            return 0.0
    
    def _calculate_modularity_gain(self, node_id: str, current_community: str, target_community: str) -> float:
        """Calculate modularity gain for community movement (simplified)"""
        
        # Simplified modularity calculation
        # In practice, use proper modularity formula
        
        # Count edges within communities vs between communities
        within_current = 0
        within_target = 0
        between = 0
        
        for neighbor_id in self.outgoing_edges.get(node_id, []) + self.incoming_edges.get(node_id, []):
            edge_key = (min(node_id, neighbor_id), max(node_id, neighbor_id))
            if edge_key in self.edges:
                edge = self.edges[edge_key]
                
                # Check if neighbor is in current community
                if neighbor_id in self._get_community_members(current_community):
                    within_current += edge.strength
                # Check if neighbor is in target community
                elif neighbor_id in self._get_community_members(target_community):
                    within_target += edge.strength
                else:
                    between += edge.strength
        
        # Simplified gain calculation
        gain = (within_target - within_current) - (between * 0.1)
        return max(0, gain)
    
    def _get_community_members(self, community_id: str) -> List[str]:
        """Get members of a community (simplified implementation)"""
        
        # This is a placeholder - in practice, maintain community membership
        return [node_id for node_id in self.nodes.keys()]  # Simplified
    
    async def _load_graph(self):
        """Load graph from database"""
        
        try:
            # Load nodes
            nodes_data = await self._load_nodes_from_db()
            for node_data in nodes_data:
                node = GraphNode(**node_data)
                self.nodes[node.id] = node
            
            # Load edges
            edges_data = await self._load_edges_from_db()
            for edge_data in edges_data:
                edge = GraphEdge(**edge_data)
                edge_key = (edge.source_id, edge.target_id)
                self.edges[edge_key] = edge
            
            logger.info(f"Loaded {len(self.nodes)} nodes and {len(self.edges)} edges from database")
            
        except Exception as e:
            logger.error(f"Error loading graph: {e}")
            raise
    
    async def _build_indices(self):
        """Build graph indices"""
        
        try:
            # Build edge indices
            for edge_key, edge in self.edges.items():
                source_id, target_id = edge_key
                
                self.outgoing_edges[source_id].append(target_id)
                self.incoming_edges[target_id].append(source_id)
                self.edge_index[edge.edge_type.value].append((source_id, target_id))
            
            # Build node property index
            for node in self.nodes.values():
                await self._update_node_indices(node)
            
            logger.info("Built graph indices")
            
        except Exception as e:
            logger.error(f"Error building indices: {e}")
            raise
    
    async def _update_node_indices(self, node: GraphNode):
        """Update indices for a node"""
        
        for key, value in node.properties.items():
            # Index string properties
            if isinstance(value, str):
                self.node_index[f"property:{key}:{value.lower()}"].add(node.id)
            
            # Index other property types
            self.node_index[f"property:{key}:{str(value)}"].add(node.id)
    
    async def _persist_node(self, node: GraphNode):
        """Persist node to database"""
        
        async def store_node(conn):
            conn.execute("""
                INSERT OR REPLACE INTO graph_nodes 
                (id, node_type, label, properties, created_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                node.id,
                node.node_type.value,
                node.label,
                json.dumps(node.properties),
                node.created_at.isoformat(),
                node.access_count,
                node.last_accessed.isoformat() if node.last_accessed else None
            ))
        
        await self.persistence_manager.execute_sql(store_node)
    
    async def _persist_edge(self, edge: GraphEdge):
        """Persist edge to database"""
        
        async def store_edge(conn):
            conn.execute("""
                INSERT OR REPLACE INTO graph_edges 
                (source_id, target_id, edge_type, strength, properties, created_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                edge.source_id,
                edge.target_id,
                edge.edge_type.value,
                edge.strength,
                json.dumps(edge.properties),
                edge.created_at.isoformat(),
                edge.access_count
            ))
        
        await self.persistence_manager.execute_sql(store_edge)
    
    async def _load_nodes_from_db(self) -> List[Dict[str, Any]]:
        """Load all nodes from database"""
        
        async def load_nodes(conn):
            cursor = conn.execute("SELECT * FROM graph_nodes")
            rows = cursor.fetchall()
            
            nodes = []
            for row in rows:
                nodes.append({
                    "id": row[0],
                    "node_type": NodeType(row[1]),
                    "label": row[2],
                    "properties": json.loads(row[3]),
                    "created_at": datetime.fromisoformat(row[4]),
                    "access_count": row[5],
                    "last_accessed": datetime.fromisoformat(row[6]) if row[6] else None
                })
            
            return nodes
        
        return await self.persistence_manager.execute_sql(load_nodes)
    
    async def _load_edges_from_db(self) -> List[Dict[str, Any]]:
        """Load all edges from database"""
        
        async def load_edges(conn):
            cursor = conn.execute("SELECT * FROM graph_edges")
            rows = cursor.fetchall()
            
            edges = []
            for row in rows:
                edges.append({
                    "source_id": row[0],
                    "target_id": row[1],
                    "edge_type": EdgeType(row[2]),
                    "strength": row[3],
                    "properties": json.loads(row[4]),
                    "created_at": datetime.fromisoformat(row[5]),
                    "access_count": row[6]
                })
            
            return edges
        
        return await self.persistence_manager.execute_sql(load_edges)
    
    async def _get_connected_components(self) -> List[List[str]]:
        """Get connected components"""
        return await self._connected_components_detection()