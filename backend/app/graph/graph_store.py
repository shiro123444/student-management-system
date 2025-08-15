"""
Graph store for JSON-based knowledge graph storage
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class GraphStore:
    """JSON-based knowledge graph storage for development/testing"""
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or settings.GRAPH_STORE_PATH
        self.graph_data = self._load_graph()
    
    def _load_graph(self) -> Dict[str, Any]:
        """Load graph data from JSON file"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load graph from {self.storage_path}: {e}")
        
        # Return empty graph structure
        return {
            "nodes": {},
            "relationships": [],
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
        }
    
    def _save_graph(self):
        """Save graph data to JSON file"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update metadata
            self.graph_data["metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.graph_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Could not save graph to {self.storage_path}: {e}")
    
    def add_node(
        self,
        node_id: str,
        labels: List[str],
        properties: Dict[str, Any]
    ) -> bool:
        """Add a node to the graph"""
        try:
            self.graph_data["nodes"][node_id] = {
                "id": node_id,
                "labels": labels,
                "properties": properties,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self._save_graph()
            logger.debug(f"Added node {node_id} with labels {labels}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add node {node_id}: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID"""
        return self.graph_data["nodes"].get(node_id)
    
    def update_node(
        self,
        node_id: str,
        properties: Dict[str, Any]
    ) -> bool:
        """Update node properties"""
        try:
            if node_id not in self.graph_data["nodes"]:
                return False
            
            self.graph_data["nodes"][node_id]["properties"].update(properties)
            self.graph_data["nodes"][node_id]["updated_at"] = datetime.utcnow().isoformat()
            
            self._save_graph()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update node {node_id}: {e}")
            return False
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node and its relationships"""
        try:
            if node_id not in self.graph_data["nodes"]:
                return False
            
            # Remove the node
            del self.graph_data["nodes"][node_id]
            
            # Remove relationships involving this node
            self.graph_data["relationships"] = [
                rel for rel in self.graph_data["relationships"]
                if rel["source"] != node_id and rel["target"] != node_id
            ]
            
            self._save_graph()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete node {node_id}: {e}")
            return False
    
    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a relationship between two nodes"""
        try:
            # Verify nodes exist
            if source_id not in self.graph_data["nodes"]:
                logger.warning(f"Source node {source_id} does not exist")
                return False
            
            if target_id not in self.graph_data["nodes"]:
                logger.warning(f"Target node {target_id} does not exist")
                return False
            
            relationship = {
                "source": source_id,
                "target": target_id,
                "type": relationship_type,
                "properties": properties or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.graph_data["relationships"].append(relationship)
            self._save_graph()
            
            logger.debug(f"Added relationship {source_id} -[{relationship_type}]-> {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            return False
    
    def find_nodes(
        self,
        labels: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Find nodes matching criteria"""
        results = []
        
        for node in self.graph_data["nodes"].values():
            # Check labels
            if labels:
                if not any(label in node["labels"] for label in labels):
                    continue
            
            # Check properties
            if properties:
                node_props = node["properties"]
                if not all(
                    key in node_props and node_props[key] == value
                    for key, value in properties.items()
                ):
                    continue
            
            results.append(node)
        
        return results
    
    def find_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find relationships matching criteria"""
        results = []
        
        for rel in self.graph_data["relationships"]:
            if source_id and rel["source"] != source_id:
                continue
            if target_id and rel["target"] != target_id:
                continue
            if relationship_type and rel["type"] != relationship_type:
                continue
            
            results.append(rel)
        
        return results
    
    def get_neighbors(
        self,
        node_id: str,
        relationship_types: Optional[List[str]] = None,
        direction: str = "both"  # "incoming", "outgoing", "both"
    ) -> List[Dict[str, Any]]:
        """Get neighboring nodes"""
        neighbors = []
        
        for rel in self.graph_data["relationships"]:
            if relationship_types and rel["type"] not in relationship_types:
                continue
            
            neighbor_id = None
            
            if direction in ["outgoing", "both"] and rel["source"] == node_id:
                neighbor_id = rel["target"]
            elif direction in ["incoming", "both"] and rel["target"] == node_id:
                neighbor_id = rel["source"]
            
            if neighbor_id and neighbor_id in self.graph_data["nodes"]:
                neighbor = self.graph_data["nodes"][neighbor_id].copy()
                neighbor["relationship"] = rel
                neighbors.append(neighbor)
        
        return neighbors
    
    def find_paths(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 3,
        relationship_types: Optional[List[str]] = None
    ) -> List[List[Dict[str, Any]]]:
        """Find paths between two nodes (simple BFS)"""
        if start_id not in self.graph_data["nodes"] or end_id not in self.graph_data["nodes"]:
            return []
        
        paths = []
        queue = [([start_id], set([start_id]))]
        
        while queue:
            current_path, visited = queue.pop(0)
            current_node = current_path[-1]
            
            if len(current_path) > max_depth:
                continue
            
            if current_node == end_id and len(current_path) > 1:
                # Convert path to node objects
                path_nodes = []
                for node_id in current_path:
                    path_nodes.append(self.graph_data["nodes"][node_id])
                paths.append(path_nodes)
                continue
            
            # Find neighbors
            neighbors = self.get_neighbors(
                current_node,
                relationship_types=relationship_types,
                direction="outgoing"
            )
            
            for neighbor in neighbors:
                neighbor_id = neighbor["id"]
                if neighbor_id not in visited:
                    new_path = current_path + [neighbor_id]
                    new_visited = visited | {neighbor_id}
                    queue.append((new_path, new_visited))
        
        return paths
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        nodes_by_label = {}
        relationships_by_type = {}
        
        # Count nodes by label
        for node in self.graph_data["nodes"].values():
            for label in node["labels"]:
                nodes_by_label[label] = nodes_by_label.get(label, 0) + 1
        
        # Count relationships by type
        for rel in self.graph_data["relationships"]:
            rel_type = rel["type"]
            relationships_by_type[rel_type] = relationships_by_type.get(rel_type, 0) + 1
        
        return {
            "total_nodes": len(self.graph_data["nodes"]),
            "total_relationships": len(self.graph_data["relationships"]),
            "nodes_by_label": nodes_by_label,
            "relationships_by_type": relationships_by_type,
            "storage_path": str(self.storage_path),
            "last_updated": self.graph_data["metadata"].get("updated_at"),
            "version": self.graph_data["metadata"].get("version")
        }
    
    def export_graph(self) -> Dict[str, Any]:
        """Export the entire graph"""
        return self.graph_data.copy()
    
    def import_graph(self, graph_data: Dict[str, Any]) -> bool:
        """Import graph data"""
        try:
            # Validate structure
            required_keys = ["nodes", "relationships", "metadata"]
            if not all(key in graph_data for key in required_keys):
                raise ValueError(f"Missing required keys: {required_keys}")
            
            self.graph_data = graph_data
            self._save_graph()
            
            logger.info("Graph data imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import graph data: {e}")
            return False
    
    def clear_graph(self) -> bool:
        """Clear all graph data"""
        try:
            self.graph_data = {
                "nodes": {},
                "relationships": [],
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
            }
            
            self._save_graph()
            logger.info("Graph data cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear graph data: {e}")
            return False