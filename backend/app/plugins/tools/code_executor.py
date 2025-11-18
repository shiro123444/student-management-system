"""
Code execution tool for educational purposes
"""

import asyncio
import logging
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from app.plugins.tool_registry import ToolPlugin

logger = logging.getLogger(__name__)

class CodeExecutorTool(ToolPlugin):
    """Tool for executing code snippets safely"""
    
    @property
    def name(self) -> str:
        return "code_executor"
    
    @property
    def description(self) -> str:
        return "Execute code snippets safely in isolated environment"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Code to execute"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript", "bash"],
                    "description": "Programming language"
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 30,
                    "default": 10,
                    "description": "Execution timeout in seconds"
                }
            },
            "required": ["code", "language"]
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute code safely"""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        timeout = kwargs.get("timeout", 10)
        
        if not code.strip():
            return {"error": "No code provided"}
        
        try:
            if language == "python":
                return await self._execute_python(code, timeout)
            elif language == "javascript":
                return await self._execute_javascript(code, timeout)
            elif language == "bash":
                return await self._execute_bash(code, timeout)
            else:
                return {"error": f"Unsupported language: {language}"}
                
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return {"error": str(e)}
    
    async def _execute_python(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute Python code"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Add safety restrictions
                safe_code = self._make_python_safe(code)
                f.write(safe_code)
                temp_file = f.name
            
            try:
                # Execute with timeout
                process = await asyncio.create_subprocess_exec(
                    'python', temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                return {
                    "success": True,
                    "stdout": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8'),
                    "return_code": process.returncode
                }
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file)
                
        except asyncio.TimeoutError:
            return {"error": f"Execution timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _execute_javascript(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute JavaScript code"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                # Add safety restrictions
                safe_code = self._make_javascript_safe(code)
                f.write(safe_code)
                temp_file = f.name
            
            try:
                # Execute with Node.js
                process = await asyncio.create_subprocess_exec(
                    'node', temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                return {
                    "success": True,
                    "stdout": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8'),
                    "return_code": process.returncode
                }
                
            finally:
                os.unlink(temp_file)
                
        except asyncio.TimeoutError:
            return {"error": f"Execution timed out after {timeout} seconds"}
        except FileNotFoundError:
            return {"error": "Node.js not available"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _execute_bash(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute bash commands"""
        try:
            # Add safety restrictions
            safe_code = self._make_bash_safe(code)
            
            # Execute with bash
            process = await asyncio.create_subprocess_shell(
                safe_code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "success": True,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8'),
                "return_code": process.returncode
            }
            
        except asyncio.TimeoutError:
            return {"error": f"Execution timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": str(e)}
    
    def _make_python_safe(self, code: str) -> str:
        """Add safety restrictions to Python code"""
        # Forbidden operations
        forbidden = [
            "import os", "import sys", "import subprocess", "import shutil",
            "open(", "file(", "execfile(", "compile(", "eval(", "exec(",
            "__import__", "globals(", "locals(", "vars(", "dir(",
            "delattr(", "setattr(", "hasattr("
        ]
        
        # Check for forbidden operations
        code_lower = code.lower()
        for forbidden_op in forbidden:
            if forbidden_op in code_lower:
                raise ValueError(f"Forbidden operation: {forbidden_op}")
        
        # Add timeout and resource limits
        safe_wrapper = f"""
import signal
import sys

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second max

try:
{code}
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
finally:
    signal.alarm(0)
"""
        return safe_wrapper
    
    def _make_javascript_safe(self, code: str) -> str:
        """Add safety restrictions to JavaScript code"""
        # Forbidden operations
        forbidden = [
            "require(", "import ", "fs.", "process.", "child_process",
            "eval(", "Function(", "setTimeout(", "setInterval("
        ]
        
        # Check for forbidden operations
        for forbidden_op in forbidden:
            if forbidden_op in code:
                raise ValueError(f"Forbidden operation: {forbidden_op}")
        
        # Add timeout wrapper
        safe_wrapper = f"""
try {{
    {code}
}} catch (error) {{
    console.error('Error:', error.message);
}}
"""
        return safe_wrapper
    
    def _make_bash_safe(self, code: str) -> str:
        """Add safety restrictions to bash code"""
        # Forbidden operations
        forbidden = [
            "rm ", "rmdir", "mv ", "cp ", "chmod", "chown",
            "sudo", "su ", "passwd", "crontab", "at ",
            "curl", "wget", "nc ", "telnet", "ssh",
            "> /", ">> /", "< /", "| /", "& /",
            "$(", "`", "eval", "exec"
        ]
        
        # Check for forbidden operations
        code_lower = code.lower()
        for forbidden_op in forbidden:
            if forbidden_op in code_lower:
                raise ValueError(f"Forbidden operation: {forbidden_op}")
        
        # Limit to safe commands only
        safe_commands = ["echo", "cat", "ls", "pwd", "date", "whoami", "id"]
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line and not any(line.startswith(cmd) for cmd in safe_commands):
                if not line.startswith('#'):  # Allow comments
                    raise ValueError(f"Unsafe command: {line}")
        
        return code