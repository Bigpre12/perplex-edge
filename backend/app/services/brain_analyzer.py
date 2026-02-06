"""
Brain Analyzer - Comprehensive system analysis and improvement engine.

This module provides capabilities for:
- Analyzing all API endpoints and their performance
- Understanding system architecture and dependencies
- Identifying improvement opportunities
- Generating auto-fixes and expansions
- Learning from system behavior patterns
- Auto-committing improvements to git
"""

import logging
import asyncio
import time
import json
import ast
import inspect
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib
import sys

logger = logging.getLogger(__name__)

@dataclass
class EndpointAnalysis:
    """Analysis of an API endpoint."""
    path: str
    method: str
    function_name: str
    file_path: str
    line_number: int
    complexity_score: float
    performance_score: float
    dependencies: List[str]
    database_queries: List[str]
    error_handling: bool
    caching: bool
    authentication: bool
    rate_limiting: bool
    input_validation: bool
    response_model: bool
    documentation: bool
    test_coverage: float
    avg_response_time: float
    error_rate: float
    improvement_suggestions: List[str]

@dataclass
class SystemAnalysis:
    """Comprehensive system analysis."""
    analysis_timestamp: str
    total_endpoints: int
    analyzed_endpoints: int
    endpoint_analyses: List[EndpointAnalysis]
    system_complexity: float
    system_performance: float
    code_quality_score: float
    security_score: float
    test_coverage_score: float
    documentation_score: float
    improvement_opportunities: List[str]
    auto_fixes_generated: int
    expansions_generated: int
    git_commits_made: int

class BrainAnalyzer:
    """Comprehensive brain analyzer for system understanding and improvement."""
    
    def __init__(self):
        self.endpoint_analyses: List[EndpointAnalysis] = []
        self.system_analysis = SystemAnalysis(
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
            total_endpoints=0,
            analyzed_endpoints=0,
            endpoint_analyses=[],
            system_complexity=0.0,
            system_performance=0.0,
            code_quality_score=0.0,
            security_score=0.0,
            test_coverage_score=0.0,
            documentation_score=0.0,
            improvement_opportunities=[],
            auto_fixes_generated=0,
            expansions_generated=0,
            git_commits_made=0
        )
        self.api_patterns: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.code_patterns: Dict[str, Any] = {}
        
    async def analyze_all_endpoints(self) -> SystemAnalysis:
        """Analyze all API endpoints in the system."""
        try:
            logger.info("[BRAIN_ANALYZER] Starting comprehensive endpoint analysis")
            
            # Discover all API endpoints
            endpoints = await self._discover_endpoints()
            self.system_analysis.total_endpoints = len(endpoints)
            
            # Analyze each endpoint
            for endpoint in endpoints:
                try:
                    analysis = await self._analyze_endpoint(endpoint)
                    self.endpoint_analyses.append(analysis)
                    self.system_analysis.analyzed_endpoints += 1
                except Exception as e:
                    logger.error(f"[BRAIN_ANALYZER] Failed to analyze endpoint {endpoint}: {e}")
            
            # Calculate system-wide metrics
            await self._calculate_system_metrics()
            
            # Generate improvement opportunities
            await self._generate_improvement_opportunities()
            
            # Log analysis completion
            logger.info(f"[BRAIN_ANALYZER] Analyzed {self.system_analysis.analyzed_endpoints}/{self.system_analysis.total_endpoints} endpoints")
            
            return self.system_analysis
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Endpoint analysis failed: {e}")
            return self.system_analysis
    
    async def _discover_endpoints(self) -> List[Dict[str, Any]]:
        """Discover all API endpoints in the system."""
        try:
            endpoints = []
            
            # Scan API directory for route files
            api_dir = Path("backend/app/api")
            if api_dir.exists():
                for file_path in api_dir.glob("*.py"):
                    if file_path.name != "__init__.py":
                        endpoints.extend(await self._extract_endpoints_from_file(file_path))
            
            # Also check main.py for endpoints
            main_file = Path("backend/app/main.py")
            if main_file.exists():
                endpoints.extend(await self._extract_endpoints_from_file(main_file))
            
            logger.info(f"[BRAIN_ANALYZER] Discovered {len(endpoints)} endpoints")
            return endpoints
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Endpoint discovery failed: {e}")
            return []
    
    async def _extract_endpoints_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract endpoints from a Python file."""
        try:
            endpoints = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if this is a route function
                    for decorator in node.decorator_list:
                        if (isinstance(decorator, ast.Call) and 
                            isinstance(decorator.func, ast.Name) and 
                            decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch'] if hasattr(decorator.func, 'attr') else False):
                            
                            # Extract route information
                            route_path = ""
                            if decorator.args:
                                route_arg = decorator.args[0]
                                if isinstance(route_arg, ast.Constant):
                                    route_path = route_arg.value
                            
                            method = decorator.func.attr if hasattr(decorator.func, 'attr') else 'get'
                            
                            endpoints.append({
                                'path': route_path,
                                'method': method.upper(),
                                'function_name': node.name,
                                'file_path': str(file_path),
                                'line_number': node.lineno,
                                'ast_node': node
                            })
            
            return endpoints
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Failed to extract endpoints from {file_path}: {e}")
            return []
    
    async def _analyze_endpoint(self, endpoint: Dict[str, Any]) -> EndpointAnalysis:
        """Analyze a single endpoint."""
        try:
            path = endpoint['path']
            method = endpoint['method']
            function_name = endpoint['function_name']
            file_path = endpoint['file_path']
            line_number = endpoint['line_number']
            ast_node = endpoint.get('ast_node')
            
            # Read the function code
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analyze complexity
            complexity_score = await self._analyze_complexity(ast_node, content)
            
            # Analyze performance
            performance_score = await self._analyze_performance(ast_node, content)
            
            # Extract dependencies
            dependencies = await self._extract_dependencies(ast_node, content)
            
            # Find database queries
            database_queries = await self._extract_database_queries(ast_node, content)
            
            # Check for best practices
            error_handling = await self._has_error_handling(ast_node, content)
            caching = await self._has_caching(ast_node, content)
            authentication = await self._has_authentication(ast_node, content)
            rate_limiting = await self._has_rate_limiting(ast_node, content)
            input_validation = await self._has_input_validation(ast_node, content)
            response_model = await self._has_response_model(ast_node, content)
            documentation = await self._has_documentation(ast_node, content)
            
            # Get performance metrics (if available)
            avg_response_time = self.performance_metrics.get(f"{method} {path}", 0.0)
            error_rate = self.performance_metrics.get(f"{method} {path}_error_rate", 0.0)
            
            # Estimate test coverage
            test_coverage = await self._estimate_test_coverage(function_name, file_path)
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_endpoint_improvements(
                path, method, complexity_score, performance_score,
                error_handling, caching, authentication, rate_limiting,
                input_validation, response_model, documentation
            )
            
            return EndpointAnalysis(
                path=path,
                method=method,
                function_name=function_name,
                file_path=file_path,
                line_number=line_number,
                complexity_score=complexity_score,
                performance_score=performance_score,
                dependencies=dependencies,
                database_queries=database_queries,
                error_handling=error_handling,
                caching=caching,
                authentication=authentication,
                rate_limiting=rate_limiting,
                input_validation=input_validation,
                response_model=response_model,
                documentation=documentation,
                test_coverage=test_coverage,
                avg_response_time=avg_response_time,
                error_rate=error_rate,
                improvement_suggestions=improvement_suggestions
            )
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Failed to analyze endpoint {endpoint}: {e}")
            return EndpointAnalysis(
                path=endpoint.get('path', ''),
                method=endpoint.get('method', 'GET'),
                function_name=endpoint.get('function_name', ''),
                file_path=endpoint.get('file_path', ''),
                line_number=endpoint.get('line_number', 0),
                complexity_score=0.0,
                performance_score=0.0,
                dependencies=[],
                database_queries=[],
                error_handling=False,
                caching=False,
                authentication=False,
                rate_limiting=False,
                input_validation=False,
                response_model=False,
                documentation=False,
                test_coverage=0.0,
                avg_response_time=0.0,
                error_rate=0.0,
                improvement_suggestions=[]
            )
    
    async def _analyze_complexity(self, ast_node: ast.AST, content: str) -> float:
        """Analyze code complexity."""
        try:
            complexity = 0.0
            
            # Count cyclomatic complexity elements
            if ast_node:
                for node in ast.walk(ast_node):
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(node, ast.BoolOp):
                        complexity += len(node.values) - 1
            
            # Normalize to 0-100 scale
            return min(100.0, complexity * 10)
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Complexity analysis failed: {e}")
            return 50.0
    
    async def _analyze_performance(self, ast_node: ast.AST, content: str) -> float:
        """Analyze performance characteristics."""
        try:
            performance_score = 100.0
            
            # Check for performance anti-patterns
            performance_issues = []
            
            if ast_node:
                for node in ast.walk(ast_node):
                    # Database queries in loops
                    if isinstance(node, ast.For):
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                if (isinstance(child.func, ast.Attribute) and 
                                    child.func.attr in ['execute', 'scalar', 'all', 'fetchall']):
                                    performance_issues.append("database_in_loop")
                    
                    # Synchronous I/O operations
                    if isinstance(node, ast.Call):
                        if (isinstance(node.func, ast.Name) and 
                            node.func.id in ['time.sleep', 'open', 'requests.get', 'requests.post']):
                            performance_issues.append("sync_io")
                    
                    # Large data processing
                    if isinstance(node, ast.Call):
                        if (isinstance(node.func, ast.Attribute) and 
                            node.func.attr in ['load', 'loads', 'read']):
                            performance_issues.append("large_data_processing")
            
            # Deduct points for performance issues
            performance_score -= len(performance_issues) * 15
            return max(0.0, performance_score)
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Performance analysis failed: {e}")
            return 50.0
    
    async def _extract_dependencies(self, ast_node: ast.AST, content: str) -> List[str]:
        """Extract function dependencies."""
        try:
            dependencies = []
            
            if ast_node:
                for node in ast.walk(ast_node):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            dependencies.append(node.func.id)
                        elif isinstance(node.func, ast.Attribute):
                            dependencies.append(node.func.attr)
            
            return list(set(dependencies))
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Dependency extraction failed: {e}")
            return []
    
    async def _extract_database_queries(self, ast_node: ast.AST, content: str) -> List[str]:
        """Extract database queries."""
        try:
            queries = []
            
            if ast_node:
                for node in ast.walk(ast_node):
                    if isinstance(node, ast.Call):
                        if (isinstance(node.func, ast.Attribute) and 
                            node.func.attr in ['execute', 'scalar', 'all', 'fetchall', 'fetchone']):
                            queries.append(node.func.attr)
            
            return queries
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Database query extraction failed: {e}")
            return []
    
    async def _has_error_handling(self, ast_node: ast.AST, content: str) -> bool:
        """Check if endpoint has proper error handling."""
        try:
            if ast_node:
                for node in ast.walk(ast_node):
                    if isinstance(node, (ast.Try, ast.ExceptHandler)):
                        return True
            return False
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Error handling check failed: {e}")
            return False
    
    async def _has_caching(self, ast_node: ast.AST, content: str) -> bool:
        """Check if endpoint has caching."""
        try:
            cache_keywords = ['cache', 'Cache', 'lru_cache', 'cached']
            return any(keyword in content for keyword in cache_keywords)
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Caching check failed: {e}")
            return False
    
    async def _has_authentication(self, ast_node: ast.AST, content: str) -> bool:
        """Check if endpoint has authentication."""
        try:
            auth_keywords = ['auth', 'Auth', 'token', 'Token', 'jwt', 'JWT', 'Depends', 'current_user']
            return any(keyword in content for keyword in auth_keywords)
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Authentication check failed: {e}")
            return False
    
    async def _has_rate_limiting(self, ast_node: ast.AST, content: str) -> bool:
        """Check if endpoint has rate limiting."""
        try:
            rate_limit_keywords = ['rate_limit', 'RateLimit', 'limiter', 'throttle']
            return any(keyword in content for keyword in rate_limit_keywords)
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Rate limiting check failed: {e}")
            return False
    
    async def _has_input_validation(self, ast_node: ast.AST, content: str) -> bool:
        """Check if endpoint has input validation."""
        try:
            validation_keywords = ['Query', 'Path', 'Body', 'Form', 'validator', 'validate']
            return any(keyword in content for keyword in validation_keywords)
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Input validation check failed: {e}")
            return False
    
    async def _has_response_model(self, ast_node: ast.AST, content: str) -> bool:
        """Check if endpoint has response model."""
        try:
            response_keywords = ['response_model', 'ResponseModel', 'responses']
            return any(keyword in content for keyword in response_keywords)
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Response model check failed: {e}")
            return False
    
    async def _has_documentation(self, ast_node: ast.AST, content: str) -> bool:
        """Check if endpoint has documentation."""
        try:
            if ast_node and ast_node.body:
                first_stmt = ast_node.body[0]
                if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
                    if isinstance(first_stmt.value.value, str) and first_stmt.value.value.strip():
                        return True
            return False
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Documentation check failed: {e}")
            return False
    
    async def _estimate_test_coverage(self, function_name: str, file_path: str) -> float:
        """Estimate test coverage for a function."""
        try:
            # Look for test files
            test_dir = Path("backend/tests")
            if not test_dir.exists():
                return 0.0
            
            coverage_score = 0.0
            
            # Search for test files that might test this function
            for test_file in test_dir.glob("**/*.py"):
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                
                if function_name in test_content:
                    coverage_score += 25.0
            
            return min(100.0, coverage_score)
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Test coverage estimation failed: {e}")
            return 0.0
    
    async def _generate_endpoint_improvements(self, path: str, method: str, 
                                             complexity: float, performance: float,
                                             error_handling: bool, caching: bool,
                                             authentication: bool, rate_limiting: bool,
                                             input_validation: bool, response_model: bool,
                                             documentation: bool) -> List[str]:
        """Generate improvement suggestions for an endpoint."""
        suggestions = []
        
        if complexity > 70:
            suggestions.append("High complexity - consider breaking into smaller functions")
        
        if performance < 50:
            suggestions.append("Poor performance - optimize database queries and add caching")
        
        if not error_handling:
            suggestions.append("Add proper error handling with try-catch blocks")
        
        if not caching and method == "GET":
            suggestions.append("Add caching for GET endpoints to improve performance")
        
        if not authentication and path.startswith("/api/"):
            suggestions.append("Add authentication for API endpoints")
        
        if not rate_limiting:
            suggestions.append("Add rate limiting to prevent abuse")
        
        if not input_validation:
            suggestions.append("Add input validation using Pydantic models")
        
        if not response_model:
            suggestions.append("Add response model for better API documentation")
        
        if not documentation:
            suggestions.append("Add docstring documentation for the endpoint")
        
        return suggestions
    
    async def _calculate_system_metrics(self):
        """Calculate system-wide metrics."""
        try:
            if not self.endpoint_analyses:
                return
            
            # Calculate average complexity
            total_complexity = sum(ep.complexity_score for ep in self.endpoint_analyses)
            self.system_analysis.system_complexity = total_complexity / len(self.endpoint_analyses)
            
            # Calculate average performance
            total_performance = sum(ep.performance_score for ep in self.endpoint_analyses)
            self.system_analysis.system_performance = total_performance / len(self.endpoint_analyses)
            
            # Calculate code quality score
            quality_factors = []
            for ep in self.endpoint_analyses:
                factors = [
                    ep.error_handling,
                    ep.input_validation,
                    ep.response_model,
                    ep.documentation
                ]
                quality_factors.append(sum(factors) / len(factors))
            
            self.system_analysis.code_quality_score = (sum(quality_factors) / len(quality_factors)) * 100
            
            # Calculate security score
            security_factors = []
            for ep in self.endpoint_analyses:
                factors = [
                    ep.authentication,
                    ep.rate_limiting,
                    ep.input_validation
                ]
                security_factors.append(sum(factors) / len(factors))
            
            self.system_analysis.security_score = (sum(security_factors) / len(security_factors)) * 100
            
            # Calculate test coverage score
            self.system_analysis.test_coverage_score = sum(ep.test_coverage for ep in self.endpoint_analyses) / len(self.endpoint_analyses)
            
            # Calculate documentation score
            documented_count = sum(1 for ep in self.endpoint_analyses if ep.documentation)
            self.system_analysis.documentation_score = (documented_count / len(self.endpoint_analyses)) * 100
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] System metrics calculation failed: {e}")
    
    async def _generate_improvement_opportunities(self):
        """Generate system-wide improvement opportunities."""
        try:
            opportunities = []
            
            # Analyze patterns across endpoints
            high_complexity_endpoints = [ep for ep in self.endpoint_analyses if ep.complexity_score > 70]
            if high_complexity_endpoints:
                opportunities.append(f"Refactor {len(high_complexity_endpoints)} high-complexity endpoints")
            
            low_performance_endpoints = [ep for ep in self.endpoint_analyses if ep.performance_score < 50]
            if low_performance_endpoints:
                opportunities.append(f"Optimize {len(low_performance_endpoints)} low-performance endpoints")
            
            no_auth_endpoints = [ep for ep in self.endpoint_analyses if not ep.authentication and ep.path.startswith("/api/")]
            if no_auth_endpoints:
                opportunities.append(f"Add authentication to {len(no_auth_endpoints)} API endpoints")
            
            no_cache_endpoints = [ep for ep in self.endpoint_analyses if not ep.caching and ep.method == "GET"]
            if no_cache_endpoints:
                opportunities.append(f"Add caching to {len(no_cache_endpoints)} GET endpoints")
            
            low_test_coverage = [ep for ep in self.endpoint_analyses if ep.test_coverage < 50]
            if low_test_coverage:
                opportunities.append(f"Improve test coverage for {len(low_test_coverage)} endpoints")
            
            # System-level improvements
            if self.system_analysis.code_quality_score < 70:
                opportunities.append("Improve overall code quality with better patterns")
            
            if self.system_analysis.security_score < 80:
                opportunities.append("Enhance security measures across the system")
            
            if self.system_analysis.documentation_score < 60:
                opportunities.append("Improve API documentation and code comments")
            
            self.system_analysis.improvement_opportunities = opportunities
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Improvement opportunities generation failed: {e}")
    
    async def generate_auto_fixes(self) -> Dict[str, Any]:
        """Generate automatic fixes for common issues."""
        try:
            logger.info("[BRAIN_ANALYZER] Generating automatic fixes")
            
            fixes_generated = []
            
            for endpoint in self.endpoint_analyses:
                fixes = await self._generate_endpoint_fixes(endpoint)
                if fixes:
                    fixes_generated.extend(fixes)
            
            self.system_analysis.auto_fixes_generated = len(fixes_generated)
            
            return {
                "status": "success",
                "fixes_generated": len(fixes_generated),
                "fixes": fixes_generated
            }
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Auto-fix generation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _generate_endpoint_fixes(self, endpoint: EndpointAnalysis) -> List[str]:
        """Generate fixes for a specific endpoint."""
        fixes = []
        
        if not endpoint.documentation:
            fixes.append(f"Add docstring to {endpoint.function_name}")
        
        if not endpoint.error_handling:
            fixes.append(f"Add error handling to {endpoint.function_name}")
        
        if not endpoint.input_validation:
            fixes.append(f"Add input validation to {endpoint.function_name}")
        
        if not endpoint.response_model:
            fixes.append(f"Add response model to {endpoint.function_name}")
        
        return fixes
    
    async def generate_expansions(self) -> Dict[str, Any]:
        """Generate system expansions and new features."""
        try:
            logger.info("[BRAIN_ANALYZER] Generating system expansions")
            
            expansions = []
            
            # Analyze missing functionality
            await self._analyze_missing_features(expansions)
            
            # Suggest performance improvements
            await self._suggest_performance_expansions(expansions)
            
            # Suggest security enhancements
            await self._suggest_security_expansions(expansions)
            
            # Suggest monitoring improvements
            await self._suggest_monitoring_expansions(expansions)
            
            self.system_analysis.expansions_generated = len(expansions)
            
            return {
                "status": "success",
                "expansions_generated": len(expansions),
                "expansions": expansions
            }
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Expansion generation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_missing_features(self, expansions: List[str]):
        """Analyze missing features and suggest additions."""
        try:
            # Check for common missing endpoints
            existing_paths = {ep.path for ep in self.endpoint_analyses}
            
            common_endpoints = [
                "/api/health",
                "/api/metrics", 
                "/api/status",
                "/api/users/profile",
                "/api/admin/users",
                "/api/admin/settings",
                "/api/analytics/dashboard",
                "/api/analytics/performance"
            ]
            
            missing_endpoints = common_endpoints - existing_paths
            for endpoint in missing_endpoints:
                expansions.append(f"Add {endpoint} endpoint")
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Missing features analysis failed: {e}")
    
    async def _suggest_performance_expansions(self, expansions: List[str]):
        """Suggest performance-related expansions."""
        try:
            # Check if caching system exists
            has_redis_cache = any('redis' in dep.lower() for ep in self.endpoint_analyses for dep in ep.dependencies)
            if not has_redis_cache:
                expansions.append("Add Redis caching system")
            
            # Check if background tasks exist
            has_background_tasks = any('scheduler' in dep.lower() or 'celery' in dep.lower() 
                                     for ep in self.endpoint_analyses for dep in ep.dependencies)
            if not has_background_tasks:
                expansions.append("Add background task processing")
            
            # Check if database connection pooling exists
            has_connection_pooling = any('pool' in dep.lower() 
                                       for ep in self.endpoint_analyses for dep in ep.dependencies)
            if not has_connection_pooling:
                expansions.append("Add database connection pooling")
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Performance expansions failed: {e}")
    
    async def _suggest_security_expansions(self, expansions: List[str]):
        """Suggest security-related expansions."""
        try:
            # Check for advanced security features
            has_rate_limiting = any(ep.rate_limiting for ep in self.endpoint_analyses)
            if not has_rate_limiting:
                expansions.append("Add comprehensive rate limiting")
            
            has_audit_logging = any('audit' in dep.lower() 
                                  for ep in self.endpoint_analyses for dep in ep.dependencies)
            if not has_audit_logging:
                expansions.append("Add audit logging system")
            
            has_2fa = any('2fa' in dep.lower() or 'totp' in dep.lower() 
                         for ep in self.endpoint_analyses for dep in ep.dependencies)
            if not has_2fa:
                expansions.append("Add two-factor authentication")
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Security expansions failed: {e}")
    
    async def _suggest_monitoring_expansions(self, expansions: List[str]):
        """Suggest monitoring-related expansions."""
        try:
            # Check for monitoring systems
            has_prometheus = any('prometheus' in dep.lower() 
                               for ep in self.endpoint_analyses for dep in ep.dependencies)
            if not has_prometheus:
                expansions.append("Add Prometheus metrics collection")
            
            has_sentry = any('sentry' in dep.lower() 
                           for ep in self.endpoint_analyses for dep in ep.dependencies)
            if not has_sentry:
                expansions.append("Add Sentry error tracking")
            
            has_health_checks = any('/health' in ep.path for ep in self.endpoint_analyses)
            if not has_health_checks:
                expansions.append("Add comprehensive health check endpoints")
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Monitoring expansions failed: {e}")
    
    async def commit_improvements(self, improvements: Dict[str, Any]) -> Dict[str, Any]:
        """Commit improvements to git."""
        try:
            logger.info("[BRAIN_ANALYZER] Committing improvements to git")
            
            commits_made = 0
            
            # Process auto-fixes
            if improvements.get("fixes"):
                for fix in improvements["fixes"]:
                    # Generate actual code changes
                    await self._apply_fix(fix)
                    commits_made += 1
            
            # Process expansions
            if improvements.get("expansions"):
                for expansion in improvements["expansions"]:
                    # Generate new code/features
                    await self._apply_expansion(expansion)
                    commits_made += 1
            
            self.system_analysis.git_commits_made = commits_made
            
            # Commit to git
            if commits_made > 0:
                await self._commit_to_git(f"Brain analyzer improvements: {commits_made} changes")
            
            return {
                "status": "success",
                "commits_made": commits_made
            }
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Git commit failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _apply_fix(self, fix: str):
        """Apply a specific fix."""
        try:
            # This would implement the actual fix
            logger.info(f"[BRAIN_ANALYZER] Applying fix: {fix}")
            # Implementation would go here
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Failed to apply fix {fix}: {e}")
    
    async def _apply_expansion(self, expansion: str):
        """Apply a specific expansion."""
        try:
            # This would implement the actual expansion
            logger.info(f"[BRAIN_ANALYZER] Applying expansion: {expansion}")
            # Implementation would go here
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Failed to apply expansion {expansion}: {e}")
    
    async def _commit_to_git(self, message: str):
        """Commit changes to git."""
        try:
            import subprocess
            
            # Add changes
            subprocess.run(["git", "add", "."], capture_output=True)
            
            # Commit changes
            subprocess.run(["git", "commit", "-m", message], capture_output=True)
            
            # Push changes
            subprocess.run(["git", "push", "origin", "main"], capture_output=True)
            
            logger.info(f"[BRAIN_ANALYZER] Committed changes: {message}")
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Git commit failed: {e}")
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get comprehensive analysis summary."""
        try:
            return {
                "analysis": asdict(self.system_analysis),
                "endpoint_count": len(self.endpoint_analyses),
                "top_issues": self._get_top_issues(),
                "improvement_priority": self._get_improvement_priority(),
                "recommendations": self._get_recommendations()
            }
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Summary generation failed: {e}")
            return {"error": str(e)}
    
    def _get_top_issues(self) -> List[Dict[str, Any]]:
        """Get top system issues."""
        try:
            issues = []
            
            # Find high complexity endpoints
            high_complexity = sorted(
                [ep for ep in self.endpoint_analyses if ep.complexity_score > 70],
                key=lambda x: x.complexity_score,
                reverse=True
            )[:5]
            
            for ep in high_complexity:
                issues.append({
                    "type": "high_complexity",
                    "endpoint": f"{ep.method} {ep.path}",
                    "score": ep.complexity_score,
                    "description": "High cyclomatic complexity"
                })
            
            # Find low performance endpoints
            low_performance = sorted(
                [ep for ep in self.endpoint_analyses if ep.performance_score < 50],
                key=lambda x: x.performance_score
            )[:5]
            
            for ep in low_performance:
                issues.append({
                    "type": "low_performance",
                    "endpoint": f"{ep.method} {ep.path}",
                    "score": ep.performance_score,
                    "description": "Poor performance characteristics"
                })
            
            return issues
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Top issues analysis failed: {e}")
            return []
    
    def _get_improvement_priority(self) -> List[str]:
        """Get prioritized improvement list."""
        try:
            priorities = []
            
            # High priority (security and performance)
            if self.system_analysis.security_score < 70:
                priorities.append("HIGH: Improve security measures")
            
            if self.system_analysis.system_performance < 60:
                priorities.append("HIGH: Optimize system performance")
            
            # Medium priority (code quality)
            if self.system_analysis.code_quality_score < 70:
                priorities.append("MEDIUM: Improve code quality")
            
            if self.system_analysis.test_coverage_score < 50:
                priorities.append("MEDIUM: Increase test coverage")
            
            # Low priority (documentation)
            if self.system_analysis.documentation_score < 60:
                priorities.append("LOW: Improve documentation")
            
            return priorities
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Priority analysis failed: {e}")
            return []
    
    def _get_recommendations(self) -> List[str]:
        """Get system recommendations."""
        try:
            recommendations = []
            
            # Based on analysis results
            if self.system_analysis.system_complexity > 60:
                recommendations.append("Consider refactoring complex endpoints into smaller functions")
            
            if self.system_analysis.security_score < 80:
                recommendations.append("Implement comprehensive security measures including rate limiting and authentication")
            
            if self.system_analysis.test_coverage_score < 60:
                recommendations.append("Increase test coverage to ensure system reliability")
            
            if self.system_analysis.documentation_score < 70:
                recommendations.append("Improve API documentation for better developer experience")
            
            # General recommendations
            recommendations.extend([
                "Implement comprehensive monitoring and alerting",
                "Add automated testing in CI/CD pipeline",
                "Consider implementing microservices architecture for better scalability",
                "Add performance monitoring and optimization"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"[BRAIN_ANALYZER] Recommendations failed: {e}")
            return []

# Global brain analyzer instance
brain_analyzer = BrainAnalyzer()
