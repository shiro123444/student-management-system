"""
Plugin registry for extensible tools and capabilities
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ToolPlugin(ABC):
    """Base class for tool plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Tool version"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get JSON schema for tool parameters"""
        pass

class ToolRegistry:
    """Registry for managing tool plugins"""
    
    def __init__(self):
        self.tools: Dict[str, ToolPlugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register_tool(self, tool: ToolPlugin) -> bool:
        """Register a new tool plugin"""
        try:
            tool_name = tool.name
            
            if tool_name in self.tools:
                logger.warning(f"Tool {tool_name} already registered, overriding")
            
            self.tools[tool_name] = tool
            logger.info(f"Registered tool: {tool_name} v{tool.version}")
            
            # Call registration hooks
            self._call_hooks("tool_registered", tool_name=tool_name, tool=tool)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool plugin"""
        if tool_name not in self.tools:
            return False
        
        del self.tools[tool_name]
        logger.info(f"Unregistered tool: {tool_name}")
        
        # Call unregistration hooks
        self._call_hooks("tool_unregistered", tool_name=tool_name)
        
        return True
    
    def get_tool(self, tool_name: str) -> Optional[ToolPlugin]:
        """Get a registered tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "version": tool.version,
                "parameters_schema": tool.get_parameters_schema()
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool not found: {tool_name}")
            
            logger.info(f"Executing tool: {tool_name}")
            
            # Call pre-execution hooks
            self._call_hooks("tool_pre_execute", tool_name=tool_name, parameters=parameters)
            
            # Execute the tool
            result = await tool.execute(**parameters)
            
            # Call post-execution hooks
            self._call_hooks("tool_post_execute", tool_name=tool_name, result=result)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            
            # Call error hooks
            self._call_hooks("tool_error", tool_name=tool_name, error=str(e))
            
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e)
            }
    
    def add_hook(self, event: str, callback: Callable):
        """Add a hook for tool events"""
        if event not in self.hooks:
            self.hooks[event] = []
        
        self.hooks[event].append(callback)
        logger.debug(f"Added hook for event: {event}")
    
    def remove_hook(self, event: str, callback: Callable):
        """Remove a hook for tool events"""
        if event in self.hooks and callback in self.hooks[event]:
            self.hooks[event].remove(callback)
            logger.debug(f"Removed hook for event: {event}")
    
    def _call_hooks(self, event: str, **kwargs):
        """Call all hooks for an event"""
        if event in self.hooks:
            for callback in self.hooks[event]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"Hook error for event {event}: {e}")
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about registered tools"""
        return {
            "total_tools": len(self.tools),
            "tools_by_name": list(self.tools.keys()),
            "hooks_registered": {
                event: len(callbacks) 
                for event, callbacks in self.hooks.items()
            }
        }

# Global tool registry instance
tool_registry = ToolRegistry()